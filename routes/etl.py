from models.database import get_db
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.etl import Customer, Product, Order
import os,shutil
import uuid
import pandas as pd
import time

etl_route=APIRouter(prefix="/ETL")

async def start_job(file_path,db,file_ext="csv"):
    try:
        # extract data from upload file
        print("process started")
        
        if file_ext=="csv":
            df=pd.read_csv(file_path)
        elif file_ext == "xls":
            df=pd.read_excel(file_path,engine="xlrd")
        else:
            df=pd.read_excel(file_path,engine="openpyxl")

        # Transformationa
        print("starting transformation job...")
        # rename columns to snake case
        df.columns=df.columns.str.lower().str.strip().str.replace(" ","_")

        # extract columns with ID to drop null values subset ID columns
        a=[i for i in df.columns if "id" in i]
        for i in df.columns:
            if "id" in i:
                a.append(i)
        print(a)
        empty_df=df.dropna(subset=a)
        print(empty_df)

        # Create customer DF and drop duplicates
        customer_df=df.loc[:,["customer_id","customer_name","segment","city","state","postal_code","region"]]
        customer_df.drop_duplicates(subset=["customer_id"],inplace=True)

        # Create Orders DF and drop duplicates
        orders_df=df.loc[:,["order_id","order_date","ship_mode","sales","quantity","discount","profit"]]
        orders_df.drop_duplicates(subset=["order_id"],inplace=True)

        # Create product DF and drop duplicates and rename sub-category column
        product_df=df.loc[:,["product_id","category","sub-category","product_name"]]
        product_df.drop_duplicates(subset=["product_id"],inplace=True)
        product_df.rename(columns={"sub-category":"sub_category"})

        # load in db
        # load customer data in database
        customer_dict=customer_df.to_dict(orient="records")
        for i in customer_dict:
            cust_id=i.get("customer_id")
            get_cust=await db.execute(select(Customer).where(Customer.customer_id==cust_id))
            result=get_cust.scalars().first()
            if result:
                print("Customer exists")
                print(result)
                continue
            customer=Customer(**i)
            db.add(customer)
        
        # load orders data in database
        order_dict=orders_df.to_dict(orient="records")
        print("loading orders data in database...")

        for i in order_dict:
            order_id=i.get("order_id")
            order=await db.execute(select(Order).where(Order.order_id==order_id))
            result=order.scalars().first()
            if result:
                print("order already exists")
                continue
            order=Order(**i)
            db.add(order)
        await db.commit()

        # load product data in database
        # product_dict=product_df.to_dict(orient="records")
        # print("loading product data in database...")
        # for i in product_dict:
        #     product_id=i.get("product_id")
        #     product=await db.execute(select(Product).where(Product.product_id==product_id))
        #     result=product.scalars().first()
            
        
        
        return {
            "status":"Completed",
            "detauls": None
        }
    except Exception as e:
        print("failed")
        print(e)
        return {
            "status":"Failed",
            "detail":f"Something went wrong: {e}"
        }

# read file from user upload, write to local fs and start etl job as background task on the file
@etl_route.post("/create_job")
async def etl_job(background_tasks:BackgroundTasks,file:UploadFile=File(...),db:AsyncSession=Depends(get_db)):
    try:
        if not file:
            raise HTTPException(status_code=422, detail="Please upload xlsx/xls or CSV file")
        cwd=os.getcwd()
        
        # write file in parent directory 
        parent_directory=os.path.dirname(cwd)
        file_path=os.path.join(parent_directory,"upload_file")
        accepted_ext=["xls","xlsx","csv"]
        file_ext=str(file.filename).split(".")[-1].lower()
        if file_ext not in accepted_ext:
            raise HTTPException(status_code=422,detail="only csv file extension supported")
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
        background_tasks.add_task(start_job,file_path,db,file_ext)
        job_id=uuid.uuid4()
        response={
            "job_id":str(job_id),
            "status":"Queued"
        }
        return JSONResponse(status_code=201, content=response)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[etl_job] something went wrong: {e}")
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")
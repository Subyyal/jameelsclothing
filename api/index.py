import os
import json
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# 1. Cloudinary Setup
cloudinary.config( 
    cloud_name = "dgizohinu", 
    api_key = "247341621751943", 
    api_secret = "lHMPrfHILJ5s_ryMfa-Fo7zELag",
    secure = True
)

DB_FILE = "products.json"

# 2. Database Helpers
def load_db():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content) if content else []
    except: return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 3. API Routes
@app.get("/api/products")
async def get_products():
    return load_db()

@app.post("/api/add-product")
async def add_product(
    title: str = Form(...),
    price: str = Form(...),
    category: str = Form(...),
    urdu_name: str = Form(None),
    image: UploadFile = File(...)
):
    upload_result = cloudinary.uploader.upload(image.file)
    image_url = upload_result["secure_url"]

    products = load_db()
    new_item = {
        "id": len(products) + 1, # Simple ID for linking
        "title": title,
        "urdu_name": urdu_name,
        "price": int(price),
        "category": category,
        "image": image_url
    }
    products.append(new_item)
    save_db(products)
    return {"status": "success"}

@app.delete("/api/delete-product/{product_id}")
async def delete_product(product_id: int):
    products = load_db()
    # Remove product by matching ID
    products = [p for p in products if p.get('id') != product_id]
    save_db(products)
    return {"status": "deleted"}

# 4. Serving HTML Files
@app.get("/")
async def home(): return FileResponse("static/index.html")

@app.get("/admin")
async def admin(): return FileResponse("static/admin.html")

@app.get("/product")
async def product_page(): return FileResponse("static/product.html")

# Mount static folder for CSS/Images
app.mount("/static", StaticFiles(directory="static"), name="static")
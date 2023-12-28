from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from ebay_scraper import scrape_ebay_info
from add_date import write_date_to_sheets
from sheets_parser import parse_sheets_links

app = FastAPI()
sheet_key = "1ctKHwRt2i95Xp7MZPcuX_I7qUKeA4T5xo3QnsQrUHgE"
credentials_file = "credentials.json"


class Item(BaseModel):
    url: str
    rowNumber: int


@app.post("/parse")
def parse_item(item: Item):
    try:
        result = scrape_ebay_info(item.url)
        write_date_to_sheets(sheet_key, result, item.rowNumber)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/updateDate")
def parse_item():
    try:
        ebay_links = parse_sheets_links(sheet_key, credentials_file)
        for ebay_link in ebay_links:
            result = scrape_ebay_info(ebay_link[1])
            write_date_to_sheets(sheet_key, result, ebay_link[0])
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

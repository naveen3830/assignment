from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import gspread
from typing import Dict
import os
from google.oauth2.service_account import Credentials
from pydantic import BaseModel

class SheetRequest(BaseModel):
    sheet_id: str

app = FastAPI(title="Sheet Analysis API",description="API for analyzing Google Sheets data and downloading results",
version="1.0.0")

scopes=["https://www.googleapis.com/auth/spreadsheets"]

credentials=Credentials.from_service_account_file(r'D:\fastapi\credentials.json',scopes=scopes)
client=gspread.authorize(credentials)

@app.post('/analyze_sheet/',response_model=Dict[str, str],tags=["Analysis"],summary="Analyze sheet data",description="Analyzes data from a Google Sheet and saves results to CSV")

def analyze(request: SheetRequest):
    try:
        sheet = client.open_by_key(request.sheet_id).sheet1
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        numeric_df = df.apply(pd.to_numeric, errors='coerce')
        results = {"Total": numeric_df.sum(),
            "Median": numeric_df.median(),
            "Mean": numeric_df.mean(),
            "Mode": numeric_df.mode().iloc[0] if not numeric_df.mode().empty else pd.Series("No mode", index=numeric_df.columns) }
        
        # updating the google sheets with calculated statistics
        for stat_name, stat_values in results.items():
            new_row = [""] * len(df.columns)
            for col_idx, col_name in enumerate(df.columns):
                if col_name in stat_values.index:
                    new_row[col_idx] = stat_values[col_name]
            sheet.append_row([stat_name] + new_row[1:])
        
        output_df = df.copy()
        for stat_name, stat_values in results.items():
            stat_row = pd.Series([""] * len(df.columns), index=df.columns)
            stat_row[stat_values.index] = stat_values
            stat_row.iloc[0] = stat_name
            output_df = pd.concat([output_df, pd.DataFrame([stat_row])], ignore_index=True)
        
        output_file = "updated_sheet.csv"
        output_df.to_csv(output_file, index=False)
        
        return {"message": "Analysis complete. Results have been updated in both Google Sheet and CSV file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/download-csv/",tags=["Downloads"],summary="Download analyzed data",description="Download the analyzed data in CSV format",response_class=FileResponse)
def download_csv():
    file_path = "updated_sheet.csv"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='text/csv', filename='updated_sheet.csv')
    raise HTTPException(status_code=404, detail="File not found")
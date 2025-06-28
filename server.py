import os
import uuid
import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from classify import classify
import uvicorn



app = FastAPI()

os.makedirs("resources", exist_ok=True)

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    try:
        df = pd.read_csv(file.file)
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")

        df["target_label"] = classify(list(zip(df["source"], df["log_message"])))
        print("Dataframe:", df.to_dict())

        output_path = f"resources/output_{uuid.uuid4().hex[:8]}.csv"
        df.to_csv(output_path, index=False)
        return FileResponse(output_path, media_type='text/csv', filename="classified_logs.csv")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import re
from django.core.files.storage import default_storage
import os

@api_view(["POST"])
def upload_file(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    file_extension = file.name.split('.')[-1].lower()
    supported_formats = {
        'csv': pd.read_csv,
        'tsv': lambda f: pd.read_csv(f, sep='\t'),
        'json': pd.read_json,
        'xlsx': lambda f: pd.read_excel(f, engine='openpyxl')
    }

    if file_extension not in supported_formats:
        return Response({"error": f"Unsupported file format: {file_extension}"}, status=400)

    try:
        # Read the file based on its extension
        data = supported_formats[file_extension](file)
        tdata = data.copy()
        error_report = detect_column_issues(tdata).to_dict(orient="list")

        # ✅ Convert DataFrame to dictionary (JSON serializable)
        json_tdata = tdata.head().to_dict(orient="list")
        info=tdata.info()
        desc=tdata.describe().to_dict(orient="list")

        return Response({"desc":desc,"info":info,"file": file.name, "error_report": error_report, "tdata": json_tdata})

    except Exception as e:
        # Handle any exceptions that might occur during file reading
        return Response({"error": f"Error processing file: {str(e)}"}, status=500)



def detect_column_issues(df):
    report = []

    for col in df.columns:

        col_data = df[col]
        col_type = "Unknown"
        errors = []

        #  Check for missing values
        missing_count = col_data.isna().sum()
        if missing_count > 0:
            errors.append(f"Missing values: {missing_count}")

        #  Attempt numeric conversion
        numeric_data = pd.to_numeric(col_data, errors='coerce')
        if numeric_data.notna().all():
            col_type = "Numeric"
        elif numeric_data.isna().sum() > 0 and numeric_data.notna().sum() > 0:
            col_type = "Mixed (Numeric & Non-Numeric)"
            errors.append("Contains non-numeric values")

        # Attempt datetime conversion (only if not already Numeric)
        if col_type == "Unknown":
            datetime_data = pd.to_datetime(col_data, errors='coerce', dayfirst=True)
            if datetime_data.notna().all():
                col_type = "Datetime"
            elif datetime_data.isna().sum() > 0 and datetime_data.notna().sum() > 0:
                col_type = "Mixed (Datetime & Non-Datetime)"
                errors.append("Contains invalid dates")

        #  Strict Time Validation (Only if all values look like time)
        time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")
        if col_data.astype(str).apply(lambda x: bool(time_pattern.match(str(x)))).all():
            col_type = "Time"
        elif col_data.astype(str).apply(lambda x: bool(time_pattern.match(str(x)))).sum() > 0:
            col_type = "Mixed (Valid & Invalid Time)"
            invalid_times = col_data.astype(str).apply(lambda x: not bool(time_pattern.match(str(x))) if isinstance(x, str) else False).sum()
            if invalid_times > 0:
                errors.append(f"Contains {invalid_times} invalid time values")

        # 5️⃣ Categorical / Text Data
        if col_type == "Unknown":
            col_type = "Categorical/Text"

        # Store the findings
        report.append({"Column": col, "Type": col_type, "Issues": ", ".join(errors) if errors else "No issues"})

    return pd.DataFrame(report)


"""
# Sample dataset with all types of data and errors
data = {
    "valid_date": ["2024-02-14", "2023-05-10", "2022-08-21"],  # Valid dates
    "invalid_date": ["2024-13-40", "not_a_date", "21/08/2022"],  # Invalid dates
    "valid_time": ["10:30:00", "15:45:20", "23:59:59"],  # Valid times
    "invalid_time": ["25:61:61", "99:99:99", "hello"],  # Invalid times
    "mixed_date_time": ["2024-02-14 10:30:00", "random_text", "2022/08/21"],  # Mixed values
    "numbers_as_strings": ["123", "45.6", "hello"],  # Mixed numbers & text
    "pure_numbers": [100, 200, 300],  # Pure numeric
    "text_only": ["apple", "banana", "orange"],  # Pure text
}

df = pd.DataFrame(data)

# Run the error detection
error_report = detect_column_issues(df)

# Print the report
print(error_report)


"""
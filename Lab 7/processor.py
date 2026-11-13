import math


WARD_NAMES = {
    "ER": "Emergency Room",
    "ICU": "Intensive Care Unit",
    "GEN": "General Ward",
    "PED": "Pediatrics",
}


def parse_vitals_summary(vitals_csv):
    if not isinstance(vitals_csv, str):
        return "Invalid vitals"
    try:
        hr, spo2, temp = map(float, vitals_csv.split(","))
    except ValueError:
        return "Invalid vitals"
    if not all(map(math.isfinite, (hr, spo2, temp))):
        return "Invalid vitals"
    if hr <= 0 or not 0 <= spo2 <= 100:
        return "Invalid vitals"

    critical = hr > 120 or spo2 < 90 or temp > 39.0
    return f"Vitals: HR={hr}, SpO2={spo2}% - {'CRITICAL' if critical else 'STABLE'}"


def compute_patient_bmi(bmi_string):
    if not isinstance(bmi_string, str):
        return None
    try:
        weight, height = map(float, bmi_string.split("/"))
    except ValueError:
        return None
    if not all(map(math.isfinite, (weight, height))):
        return None
    if weight <= 0 or height <= 0:
        return None
    try:
        bmi = weight / height**2
    except (OverflowError, ZeroDivisionError):
        return None
    return round(bmi, 2) if math.isfinite(bmi) else None


def assign_ward_bed(allocation_code):
    if not isinstance(allocation_code, str):
        return "Invalid allocation"
    try:
        ward, bed_str = allocation_code.strip().split("-")
        bed_num = int(bed_str)
    except ValueError:
        return "Invalid allocation"
    ward_name = WARD_NAMES.get(ward.upper())
    if ward_name is None or bed_num <= 0:
        return "Invalid allocation"
    return f"{ward_name} Bed #{bed_num}"


def main():
    try:
        print("==== Running parse_vitals_summary ====")
        v_input = input("Enter vitals (HR,SpO2,Temp): ")
        print("Summary:", parse_vitals_summary(v_input))

        print("\n==== Running compute_patient_bmi ====")
        b_input = input("Enter weight/height (e.g. 70/1.75): ")
        bmi = compute_patient_bmi(b_input)
        print("BMI:", bmi if bmi is not None else "Invalid measurements")

        print("\n==== Running assign_ward_bed ====")
        w_input = input("Enter allocation (e.g. ICU-05): ")
        print("Assignment:", assign_ward_bed(w_input))
    except EOFError:
        print("Input ended.")


if __name__ == "__main__":
    main()


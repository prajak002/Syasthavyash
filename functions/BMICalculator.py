def BMI(height,weight):
    height=int(height)
    weight=int(weight)
    bmi= weight/(height*0.01*height*0.01)
    bmi=round(bmi)
    if bmi< 19:
        status="Underweight"
    elif bmi>19 and bmi <26:
        status="Healthy"
    else:
        status="Overweight"
    return bmi,status
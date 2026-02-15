def get_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def main():
    scores = [95, 87, 72, 65, 58]

    for score in scores:
        grade = get_grade(score)
        print(f"Score {score} = Grade {grade}")


if __name__ == "__main__":
    main()


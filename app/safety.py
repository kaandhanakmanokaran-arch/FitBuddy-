def safety_context(age: int, goal: str) -> str:
    if age < 18:
        return (
            "The user is under 18. Provide age-appropriate general movement and wellbeing "
            "guidance. Do not recommend calorie restriction, weight-loss targets, body-fat "
            "targets, supplements, fasting, extreme exercise, or body-comparison goals. "
            "Encourage a parent/guardian, qualified coach, or healthcare professional when "
            "appropriate."
        )
    return (
        "Provide general wellness information only. Do not diagnose or treat medical conditions. "
        "Avoid extreme exercise, crash dieting, unsafe supplement advice, or unrealistic promises. "
        "If pain, injury, illness, or a medical condition is mentioned, recommend professional guidance."
    )

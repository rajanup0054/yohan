import pandas as pd
import numpy as np

# Seed for reproducibility
np.random.seed(42)

# Generate random data
data = {
    "interaction_count": np.random.randint(20, 300, 120),
    "quiz_scores": np.random.randint(50, 100, 120),
    "completion_rate": np.random.randint(30, 100, 120),
}

# Create engagement levels based on conditions
conditions = [
    (data["interaction_count"] > 200) & (data["quiz_scores"] > 80) & (data["completion_rate"] > 75),
    (data["interaction_count"] > 100) & (data["quiz_scores"] > 70) & (data["completion_rate"] > 50),
]
choices = ["high", "medium"]
data["engagement_level"] = np.select(conditions, choices, default="low")

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("sample_student_data.csv", index=False)

print("Sample dataset generated and saved as 'sample_student_data.csv'")

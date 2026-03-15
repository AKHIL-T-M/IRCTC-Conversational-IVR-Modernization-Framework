from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

labels = [
    "pnr status",
    "ticket booking",
    "cancel ticket",
    "train availability",
    "customer care"
]

def detect_intent(text):

    result = classifier(text, labels)

    return result["labels"][0]
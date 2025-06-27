import requests
import base64
import json

# API endpoint
url = "http://localhost:8000/ocr"


# Load image file
def load_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Example usage
def main():
    try:
        # Replace with your image path
        image_path = "sample_image.png"

        # Encode image
        base64_image = load_image(image_path)

        # Prepare request
        payload = {
            "image_data": base64_image
        }

        # Send request
        response = requests.post(url, json=payload)

        # Process response
        if response.status_code == 200:
            result = response.json()
            print("Status:", result["status"])

            if result["status"] == "success":
                print("OCR Results:")
                for i, text in enumerate(result["text_list"]):
                    print(f"{i + 1}. {text}")
            else:
                print("Error:", result["error_message"])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
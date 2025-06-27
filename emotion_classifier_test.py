from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager

if __name__ == "__main__":
    manager = EmotionClassifierManager()

    # 단일 파일 처리
    print(manager.classify_from_file("emotion_classifier/input1.txt", "emotion_classifier/output/result1.txt"))

    # 배치 처리
    batch_results = manager.classify_batch(
        input_paths=["emotion_classifier/input1.txt", "emotion_classifier/input2.txt"],
        output_dir="emotion_classifier/batch_outputs"
    )
    for path, result in batch_results.items():
        print(f"{path}: {result}")
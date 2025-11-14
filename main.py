from parser.splitter import demo_on_text
from parser.logic import analyze_scene

def main():
    with open("data/example.txt", "r", encoding="utf-8") as f:
        text = f.read()

    results = demo_on_text(text)
    for header, scene_text in results:
        print("=" * 60)
        print(header)
        print("-" * 60)
        data = analyze_scene(scene_text)
        for key, value in data.items():
            if isinstance(value, list):
                print(f"{key}: {', '.join(value) if value else '-'}")
            else:
                print(f"{key}: {value}")
        print("\n")

if __name__ == "__main__":
    main()

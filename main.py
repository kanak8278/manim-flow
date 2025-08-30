"""
ManimFlow - A pipeline for generating Manim animations in 3Blue1Brown style

Main entry point for the ManimFlow animation generation system.
"""

def main():
    print("Welcome to ManimFlow!")
    print("A pipeline for generating Manim animations in 3Blue1Brown style")
    print("\nAvailable scenes:")
    print("- fixed_opening.py: Working projectile physics opening")
    print("- opening_scene.py: Original bouncing ball demo")
    print("- butterfly_curve.py: Beautiful butterfly curve animation")
    print("- butterfly_enhanced.py: Component-by-component butterfly analysis")
    print("  * ButterflyEnhanced: Progressive curve building")
    print("  * ButterflyAnalysis: Mathematical component breakdown")
    print("- butterfly_improved.py: Detailed educational butterfly analysis")
    print("  * ButterflyImproved: Comprehensive explanation with proper pacing")
    print("- butterfly_final.py: ⭐ FINAL VERSION - Perfect butterfly visualization")
    print("  * ButterflyFinal: Complete 2π loops, clean text, color transitions")
    print("\nTo render: uv run python -m manim -pqh <scene_file>.py <SceneClass>")


if __name__ == "__main__":
    main()

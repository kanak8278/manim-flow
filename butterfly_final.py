from manim import *
import numpy as np

class ButterflyFinal(Scene):
    def construct(self):
        # Set black background
        self.camera.background_color = BLACK
        
        # ==================== INTRODUCTION ====================
        
        # Main title
        main_title = Text("The Butterfly Curve", font_size=52, weight=BOLD)
        main_title.set_color_by_gradient(PINK, PURPLE, BLUE)
        main_title.move_to(UP * 2.5)
        
        # Full equation - start large
        full_equation = Text(
            "r = e^(sin θ) - 2cos(4θ) + sin^5((2θ - π)/24)",
            font_size=32
        )
        full_equation.set_color(WHITE)
        full_equation.move_to(UP * 1.5)
        
        # Show introduction
        self.play(Write(main_title), run_time=2)
        self.wait(1)
        self.play(Write(full_equation), run_time=2.5)
        self.wait(2)
        
        # Brief polar explanation
        polar_text = Text("In polar coordinates: r = distance, θ = angle", 
                         font_size=24, color=YELLOW)
        polar_text.move_to(UP * 0.8)
        self.play(Write(polar_text), run_time=2)
        self.wait(1.5)
        
        # Clear for component analysis
        self.play(
            FadeOut(main_title),
            FadeOut(polar_text),
            run_time=1.5
        )
        
        # Move equation up and make smaller
        self.play(
            full_equation.animate.scale(0.7).move_to(UP * 3.2),
            run_time=1.5
        )
        
        # ==================== SETUP AXES ====================
        
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2.5, 2.5, 1],
            x_length=7,
            y_length=5.5,
            axis_config={"stroke_width": 2, "stroke_opacity": 0.5}
        ).move_to(DOWN * 0.3)
        
        self.play(Create(axes), run_time=1.5)
        
        # ==================== COMPONENT FUNCTIONS ====================
        
        def component1(theta):
            return np.exp(np.sin(theta))
        
        def component2(theta):
            return 2 * np.cos(4 * theta)
        
        def component3(theta):
            return np.sin((2 * theta - PI) / 24) ** 5
        
        def combined_r(theta, use_comp1=True, use_comp2=True, use_comp3=True):
            r = 0
            if use_comp1:
                r += component1(theta)
            if use_comp2:
                r -= component2(theta)
            if use_comp3:
                r += component3(theta)
            return r
        
        def polar_to_cartesian(theta, r_func, **kwargs):
            r = r_func(theta, **kwargs)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            return np.array([x, y, 0])
        
        # ==================== COMPONENT 1: e^(sin θ) ====================
        
        # Highlight first component in equation
        highlighted_eq1 = Text(
            "r = e^(sin θ) - 2cos(4θ) + sin^5((2θ - π)/24)",
            font_size=22
        )
        highlighted_eq1[4:12].set_color(GREEN)  # Highlight e^(sin θ)
        highlighted_eq1.move_to(UP * 3.2)
        
        self.play(Transform(full_equation, highlighted_eq1), run_time=1.5)
        
        # Component 1 title
        comp1_title = Text("Component 1: e^(sin θ)", font_size=36, weight=BOLD, color=GREEN)
        comp1_title.move_to(UP * 2.5)
        
        self.play(Write(comp1_title), run_time=1.5)
        self.wait(0.5)
        
        # Show first explanation
        exp1 = Text("Creates smooth radial expansion and contraction", 
                   font_size=20, color=WHITE)
        exp1.move_to(UP * 2.0)
        
        self.play(Write(exp1), run_time=1.5)
        self.wait(1)
        
        # Draw component 1 curve with multiple loops
        curve1 = ParametricFunction(
            lambda t: polar_to_cartesian(t, combined_r, use_comp1=True, use_comp2=False, use_comp3=False),
            t_range=[0, 4*PI, 0.02],
            stroke_width=4,
            color=GREEN
        ).move_to(axes.get_center()).scale(0.25)
        
        self.play(Create(curve1), run_time=4, rate_func=linear)
        
        # Show more detail
        exp2 = Text("Range: e^(-1) ≈ 0.37 to e^1 ≈ 2.72", 
                   font_size=18, color=GRAY)
        exp2.move_to(UP * 1.7)
        
        self.play(Write(exp2), run_time=1.5)
        self.wait(2)
        
        # Clear text for next component
        self.play(
            FadeOut(comp1_title),
            FadeOut(exp1), 
            FadeOut(exp2),
            run_time=1.5
        )
        
        # ==================== COMPONENT 2: -2cos(4θ) ====================
        
        # Highlight second component
        highlighted_eq2 = Text(
            "r = e^(sin θ) - 2cos(4θ) + sin^5((2θ - π)/24)",
            font_size=22
        )
        highlighted_eq2[4:12].set_color(GREEN)  # Keep first highlighted
        highlighted_eq2[15:24].set_color(BLUE)  # Highlight -2cos(4θ)
        highlighted_eq2.move_to(UP * 3.2)
        
        self.play(Transform(full_equation, highlighted_eq2), run_time=1.5)
        
        # Component 2 title
        comp2_title = Text("Component 2: Adding -2cos(4θ)", font_size=36, weight=BOLD, color=BLUE)
        comp2_title.move_to(UP * 2.5)
        
        self.play(Write(comp2_title), run_time=1.5)
        
        # Explanation
        exp3 = Text("Four oscillations per rotation create detailed structure", 
                   font_size=20, color=WHITE)
        exp3.move_to(UP * 2.0)
        
        self.play(Write(exp3), run_time=1.5)
        self.wait(1)
        
        # Transform to component 1+2
        curve2 = ParametricFunction(
            lambda t: polar_to_cartesian(t, combined_r, use_comp1=True, use_comp2=True, use_comp3=False),
            t_range=[0, 4*PI, 0.02],
            stroke_width=4,
            color=BLUE
        ).move_to(axes.get_center()).scale(0.25)
        
        self.play(Transform(curve1, curve2), run_time=5, rate_func=smooth)
        
        # Show detail
        exp4 = Text("Creates four-fold symmetry and 'pinching' effects", 
                   font_size=18, color=GRAY)
        exp4.move_to(UP * 1.7)
        
        self.play(Write(exp4), run_time=1.5)
        self.wait(2)
        
        # Clear text
        self.play(
            FadeOut(comp2_title),
            FadeOut(exp3),
            FadeOut(exp4),
            run_time=1.5
        )
        
        # ==================== COMPONENT 3: sin^5((2θ - π)/24) ====================
        
        # Highlight third component
        highlighted_eq3 = Text(
            "r = e^(sin θ) - 2cos(4θ) + sin^5((2θ - π)/24)",
            font_size=22
        )
        highlighted_eq3[4:12].set_color(GREEN)
        highlighted_eq3[15:24].set_color(BLUE)
        highlighted_eq3[27:].set_color(PINK)  # Highlight last component
        highlighted_eq3.move_to(UP * 3.2)
        
        self.play(Transform(full_equation, highlighted_eq3), run_time=1.5)
        
        # Component 3 title
        comp3_title = Text("Component 3: The Butterfly Touch", font_size=36, weight=BOLD, color=PINK)
        comp3_title.move_to(UP * 2.5)
        
        self.play(Write(comp3_title), run_time=1.5)
        
        # Explanation
        exp5 = Text("Subtle slow modulation creates butterfly asymmetry", 
                   font_size=20, color=WHITE)
        exp5.move_to(UP * 2.0)
        
        self.play(Write(exp5), run_time=1.5)
        self.wait(1)
        
        # Transform to final curve with extended range for butterfly
        final_curve = ParametricFunction(
            lambda t: polar_to_cartesian(t, combined_r, use_comp1=True, use_comp2=True, use_comp3=True),
            t_range=[0, 12*PI, 0.01],
            stroke_width=4,
            color=PINK
        ).move_to(axes.get_center()).scale(0.25)
        
        self.play(Transform(curve1, final_curve), run_time=6, rate_func=smooth)
        
        # Show detail
        exp6 = Text("Very low frequency: 1/12 cycle creates wing asymmetry", 
                   font_size=18, color=GRAY)
        exp6.move_to(UP * 1.7)
        
        self.play(Write(exp6), run_time=1.5)
        self.wait(3)
        
        # Clear everything for final presentation
        self.play(
            FadeOut(comp3_title),
            FadeOut(exp5),
            FadeOut(exp6),
            FadeOut(axes),
            run_time=2
        )
        
        # ==================== FINAL PRESENTATION ====================
        
        # Zoom out equation
        final_equation = Text(
            "r = e^(sin θ) - 2cos(4θ) + sin^5((2θ - π)/24)",
            font_size=28
        )
        final_equation.set_color_by_gradient(GREEN, BLUE, PINK)
        final_equation.move_to(UP * 3.2)
        
        self.play(Transform(full_equation, final_equation), run_time=1.5)
        
        # Final title
        final_title = Text("The Complete Butterfly Curve", font_size=44, weight=BOLD)
        final_title.set_color_by_gradient(PINK, PURPLE, BLUE)
        final_title.move_to(UP * 2.5)
        
        self.play(Write(final_title), run_time=1.5)
        
        # Scale up and center the curve
        self.play(
            curve1.animate.scale(3.5).move_to(ORIGIN),
            run_time=2
        )
        
        # ==================== COLOR TRANSITION BUTTERFLY BUILD ====================
        
        # Create color-transitioning version
        butterfly_segments = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK]
        
        for i, color in enumerate(colors):
            segment = ParametricFunction(
                lambda t: polar_to_cartesian(t, combined_r, use_comp1=True, use_comp2=True, use_comp3=True),
                t_range=[i*12*PI/7, (i+1)*12*PI/7, 0.02],
                stroke_width=5,
                color=color
            ).scale(0.875).move_to(ORIGIN)  # 0.25 * 3.5 = 0.875
            butterfly_segments.append(segment)
        
        # Clear current curve and build new one with colors
        self.play(FadeOut(curve1), run_time=1)
        
        # Build butterfly with color transitions
        current_segments = VGroup()
        for segment in butterfly_segments:
            current_segments.add(segment)
            self.play(Create(segment), run_time=1.2, rate_func=linear)
        
        # Mathematical summary
        summary = Text("Three Mathematical Forces Combined into Art", 
                      font_size=26, color=WHITE)
        summary.move_to(DOWN * 3.2)
        
        self.play(Write(summary), run_time=2)
        self.wait(2)
        
        # Final rotation with all colors
        self.play(
            Rotate(current_segments, angle=2*PI),
            run_time=8,
            rate_func=smooth
        )
        
        # Hold final scene
        self.wait(4)
        
        # Final fadeout
        everything = Group(full_equation, final_title, current_segments, summary)
        self.play(FadeOut(everything), run_time=3)

# ManimFlow - Final Butterfly Curve with Proper Text Management and Color Transitions
# To render: uv run python -m manim -pqh butterfly_final.py ButterflyFinal
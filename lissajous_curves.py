from manim import *
import numpy as np

class LissajousCurvesComplete(Scene):
    def construct(self):
        # Set black background
        self.camera.background_color = BLACK
        
        # ==================== ACT 1: THE HOOK (0:00 - 0:45) ====================
        
        # Opening mystery questions
        question1 = Text("What happens when frequencies dance?", font_size=36, color=WHITE)
        question1.move_to(ORIGIN)
        
        self.play(Write(question1), run_time=1.5)
        self.wait(1.5)
        
        # Transform to second question
        question2 = Text("Can mathematics create music?", font_size=36)
        question2.set_color_by_gradient(WHITE, BLUE)
        question2.move_to(ORIGIN)
        
        self.play(Transform(question1, question2), run_time=1.5)
        self.wait(1.5)
        
        # Fade to discovery text
        discovery = Text("Let's discover the dance...", font_size=32, color=YELLOW)
        discovery.move_to(ORIGIN)
        
        self.play(FadeOut(question1), run_time=1)
        self.play(Write(discovery), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(discovery), run_time=0.5)
        
        # Preview: Show complex 3:4 ratio Lissajous with phase evolution
        def lissajous_preview(t, a=3, b=4, delta=0):
            x = 2 * np.sin(a * t + delta)
            y = 2 * np.sin(b * t)
            return np.array([x, y, 0])
        
        # Create evolving preview curve
        preview_curve = ParametricFunction(
            lambda t: lissajous_preview(t, 3, 4, 0),
            t_range=[0, 4*PI, 0.01],
            stroke_width=4,
            color=PURPLE
        ).scale(0.8)
        
        self.play(Create(preview_curve), run_time=3)
        
        # Phase evolution preview
        for delta in [PI/4, PI/2, 3*PI/4, PI]:
            new_curve = ParametricFunction(
                lambda t: lissajous_preview(t, 3, 4, delta),
                t_range=[0, 4*PI, 0.01],
                stroke_width=4,
                color=PURPLE
            ).scale(0.8)
            self.play(Transform(preview_curve, new_curve), run_time=1)
            self.wait(0.3)
        
        self.wait(0.5)
        self.play(FadeOut(preview_curve), run_time=1)
        
        # Main title appears
        main_title = Text("Lissajous Curves", font_size=56, weight=BOLD)
        main_title.set_color_by_gradient(BLUE, PURPLE, RED)
        main_title.move_to(UP * 0.5)
        
        subtitle = Text("The Dance of Frequencies", font_size=28)
        subtitle.set_color(YELLOW)
        subtitle.move_to(DOWN * 0.5)
        
        self.play(Write(main_title), run_time=2)
        self.play(Write(subtitle), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(main_title), FadeOut(subtitle), run_time=1)
        
        # ==================== ACT 2: MATHEMATICAL FOUNDATION (0:45 - 1:45) ====================
        
        # Foundation title
        foundation_title = Text("Mathematical Foundation", font_size=36, color=BLUE)
        foundation_title.move_to(UP * 2.7)
        
        self.play(Write(foundation_title), run_time=1.5)
        self.wait(1)
        
        # Show parametric equations cleanly
        x_eq = Text("x(t) = A*sin(a*t + d)", font_size=32, color=WHITE)
        x_eq.move_to(UP * 1.2)
        
        y_eq = Text("y(t) = B*sin(b*t)", font_size=32, color=WHITE)
        y_eq.move_to(UP * 0.4)
        
        self.play(Write(x_eq), run_time=2)
        self.wait(1)
        self.play(Write(y_eq), run_time=2)
        self.wait(1)
        
        # Parameter explanations
        param_explanations = VGroup(
            Text("A, B: Amplitudes", font_size=20, color=GREEN),
            Text("a, b: Frequencies", font_size=20, color=BLUE), 
            Text("d: Phase shift", font_size=20, color=RED)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        param_explanations.move_to(DOWN * 1.2)
        
        self.play(Write(param_explanations), run_time=2)
        self.wait(2)
        
        # Clean up foundation section
        self.play(
            FadeOut(foundation_title),
            FadeOut(x_eq),
            FadeOut(y_eq),
            FadeOut(param_explanations),
            run_time=1.5
        )
        
        # ==================== ACT 3: COMPONENT BUILDING (1:45 - 3:15) ====================
        
        # Set up coordinate system
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            axis_config={"color": GRAY}
        ).move_to(DOWN * 0.3)
        
        axis_labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        self.play(Create(axes), Write(axis_labels), run_time=2)
        self.wait(0.5)
        
        # Component 1: 1:1 ratio (circle/ellipse)
        comp1_title = Text("Component 1: Equal Frequencies", font_size=30, color=GREEN)
        comp1_title.move_to(UP * 2.7)
        
        comp1_details = Text("a = 1, b = 1 (ratio 1:1)", font_size=18, color=GREEN)
        comp1_details.move_to(UP * 2.2)
        
        self.play(Write(comp1_title), Write(comp1_details), run_time=2)
        self.wait(1)
        
        def lissajous_11(t, delta=0):
            x = 2 * np.sin(t + delta)
            y = 2 * np.sin(t)
            return np.array([x, y, 0])
        
        # Show phase evolution from circle to line
        for delta in [0, PI/4, PI/2]:
            curve_11 = ParametricFunction(
                lambda t: lissajous_11(t, delta),
                t_range=[0, 2*PI, 0.01],
                stroke_width=4,
                color=GREEN
            ).move_to(DOWN * 0.3)
            
            if delta == 0:
                self.play(Create(curve_11), run_time=4)
            else:
                prev_curve = curve_11_prev if 'curve_11_prev' in locals() else curve_11
                self.play(Transform(prev_curve, curve_11), run_time=2)
            
            curve_11_prev = curve_11
            self.wait(0.8)
        
        # Clean up component 1
        self.play(
            FadeOut(comp1_title),
            FadeOut(comp1_details),
            FadeOut(curve_11_prev),
            run_time=1.5
        )
        
        # Component 2: 2:1 ratio (figure-8)
        comp2_title = Text("Component 2: Double Frequency", font_size=30, color=BLUE)
        comp2_title.move_to(UP * 2.7)
        
        comp2_details = Text("a = 2, b = 1 (ratio 2:1)", font_size=18, color=BLUE)
        comp2_details.move_to(UP * 2.2)
        
        self.play(Write(comp2_title), Write(comp2_details), run_time=2)
        self.wait(1)
        
        def lissajous_21(t, delta=0):
            x = 2 * np.sin(2*t + delta)
            y = 2 * np.sin(t)
            return np.array([x, y, 0])
        
        curve_21 = ParametricFunction(
            lambda t: lissajous_21(t, 0),
            t_range=[0, 2*PI, 0.01],
            stroke_width=4,
            color=BLUE
        ).move_to(DOWN * 0.3)
        
        self.play(Create(curve_21), run_time=4)
        self.wait(1.5)
        
        # Show phase shift effect
        curve_21_shifted = ParametricFunction(
            lambda t: lissajous_21(t, PI/2),
            t_range=[0, 2*PI, 0.01],
            stroke_width=4,
            color=BLUE
        ).move_to(DOWN * 0.3)
        
        self.play(Transform(curve_21, curve_21_shifted), run_time=2)
        self.wait(1)
        
        # Clean up component 2  
        self.play(
            FadeOut(comp2_title),
            FadeOut(comp2_details),
            FadeOut(curve_21),
            run_time=1.5
        )
        
        # Component 3: 3:2 ratio (more complex knot)
        comp3_title = Text("Component 3: Complex Harmonies", font_size=30, color=PURPLE)
        comp3_title.move_to(UP * 2.7)
        
        comp3_details = Text("a = 3, b = 2 (ratio 3:2)", font_size=18, color=PURPLE)
        comp3_details.move_to(UP * 2.2)
        
        self.play(Write(comp3_title), Write(comp3_details), run_time=2)
        self.wait(1)
        
        def lissajous_32(t, delta=0):
            x = 2 * np.sin(3*t + delta)
            y = 2 * np.sin(2*t)
            return np.array([x, y, 0])
        
        curve_32 = ParametricFunction(
            lambda t: lissajous_32(t, 0),
            t_range=[0, 2*PI, 0.01],
            stroke_width=4,
            color=PURPLE
        ).move_to(DOWN * 0.3)
        
        self.play(Create(curve_32), run_time=5)
        self.wait(2)
        
        # Clean up component 3
        self.play(
            FadeOut(comp3_title),
            FadeOut(comp3_details),
            FadeOut(curve_32),
            run_time=1.5
        )
        
        # Clean up axes for next section
        self.play(FadeOut(axes), FadeOut(axis_labels), run_time=1)
        
        # ==================== ACT 4: MATHEMATICAL ANALYSIS (3:15 - 4:15) ====================
        
        analysis_title = Text("Phase Evolution Analysis", font_size=36, color=YELLOW)
        analysis_title.move_to(UP * 2.7)
        
        self.play(Write(analysis_title), run_time=1.5)
        self.wait(1)
        
        # Create smaller coordinate system for analysis
        analysis_axes = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            x_length=5,
            y_length=5,
            axis_config={"color": GRAY, "stroke_width": 2}
        ).move_to(ORIGIN)
        
        self.play(Create(analysis_axes), run_time=1.5)
        
        # Show phase evolution for 2:3 ratio
        phase_label = Text("d = 0", font_size=24, color=WHITE)
        phase_label.move_to(UP * 1.8)
        self.play(Write(phase_label), run_time=0.5)
        
        def lissajous_23(t, delta=0):
            x = 1.8 * np.sin(2*t + delta)
            y = 1.8 * np.sin(3*t)
            return np.array([x, y, 0])
        
        # Initial curve
        analysis_curve = ParametricFunction(
            lambda t: lissajous_23(t, 0),
            t_range=[0, 2*PI, 0.01],
            stroke_width=3,
            color=RED
        )
        
        self.play(Create(analysis_curve), run_time=4)
        self.wait(1)
        
        # Phase evolution
        deltas = [PI/4, PI/2, 3*PI/4, PI, 5*PI/4, 3*PI/2, 7*PI/4, 2*PI]
        delta_labels = ["pi/4", "pi/2", "3pi/4", "pi", "5pi/4", "3pi/2", "7pi/4", "2pi"]
        
        for delta, delta_text in zip(deltas, delta_labels):
            new_phase_label = Text(f"d = {delta_text}", font_size=24, color=WHITE)
            new_phase_label.move_to(UP * 1.8)
            
            new_curve = ParametricFunction(
                lambda t: lissajous_23(t, delta),
                t_range=[0, 2*PI, 0.01],
                stroke_width=3,
                color=RED
            )
            
            self.play(
                Transform(phase_label, new_phase_label),
                Transform(analysis_curve, new_curve),
                run_time=0.8
            )
            self.wait(0.2)
        
        self.wait(1.5)
        
        # Clean up analysis section
        self.play(
            FadeOut(analysis_title),
            FadeOut(phase_label),
            FadeOut(analysis_curve),
            FadeOut(analysis_axes),
            run_time=1.5
        )
        
        # ==================== ACT 5: GRAND FINALE (4:15 - 5:30) ====================
        
        # Finale title
        finale_title = Text("The Grand Dance", font_size=42, weight=BOLD)
        finale_title.set_color_by_gradient(RED, PURPLE, BLUE)
        finale_title.move_to(UP * 2.7)
        
        self.play(Write(finale_title), run_time=2)
        self.wait(1)
        
        # Create grid of different ratio curves
        finale_axes = Axes(
            x_range=[-4, 4, 2],
            y_range=[-4, 4, 2],
            x_length=8,
            y_length=8,
            axis_config={"color": GRAY, "stroke_width": 1}
        ).move_to(DOWN * 0.5)
        
        self.play(Create(finale_axes), run_time=1.5)
        
        # Multiple curves with different ratios and colors
        ratios = [(1,1), (2,1), (3,2), (4,3), (5,4)]
        colors = [GREEN, BLUE, PURPLE, RED, ORANGE]
        curves = []
        
        for (a, b), color in zip(ratios, colors):
            def make_liss_func(a_val, b_val):
                def liss_func(t):
                    x = 2.5 * np.sin(a_val * t)
                    y = 2.5 * np.sin(b_val * t)
                    return np.array([x, y, 0])
                return liss_func
            
            curve = ParametricFunction(
                make_liss_func(a, b),
                t_range=[0, 2*PI, 0.01],
                stroke_width=2,
                color=color
            ).move_to(DOWN * 0.5)
            
            curves.append(curve)
        
        # Animate all curves simultaneously with staggered start
        animations = []
        for i, curve in enumerate(curves):
            animations.append(Create(curve))
        
        # Create curves one by one with overlapping timing
        for i, curve in enumerate(curves):
            self.play(Create(curve), run_time=1.5)
            if i < len(curves) - 1:
                self.wait(0.3)
        
        self.wait(2)
        
        # Rainbow evolution of the most complex curve
        final_curve = curves[-1]  # 5:4 ratio
        
        rainbow_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK]
        
        for color in rainbow_colors:
            new_curve = ParametricFunction(
                make_liss_func(5, 4),
                t_range=[0, 2*PI, 0.01],
                stroke_width=4,
                color=color
            ).move_to(DOWN * 0.5)
            
            self.play(Transform(final_curve, new_curve), run_time=0.5)
            self.wait(0.15)
        
        self.wait(1.5)
        
        # Clean up for final message
        self.play(
            FadeOut(finale_title),
            *[FadeOut(curve) for curve in curves[:-1]],
            FadeOut(final_curve),
            FadeOut(finale_axes),
            run_time=2
        )
        
        # Final message with music note emoji (using VGroup structure)
        math_text = Text("Mathematics + Harmony = ", font_size=36, color=WHITE)
        music_emoji = Text("♪", font_size=48)  # Using simpler music symbol
        music_emoji.set_color(BLUE)
        
        final_message = VGroup(math_text, music_emoji).arrange(RIGHT, buff=0.2)
        final_message.move_to(ORIGIN)
        final_message.set_color_by_gradient(RED, BLUE, PURPLE)
        
        self.play(Write(final_message), run_time=3)
        self.wait(2)
        
        # Pulsing finale effect
        for _ in range(4):
            self.play(
                final_message.animate.scale(1.1),
                run_time=0.4,
                rate_func=smooth
            )
            self.play(
                final_message.animate.scale(1/1.1),
                run_time=0.4,
                rate_func=smooth
            )
        
        self.wait(2)
        
        # Fade out
        self.play(FadeOut(final_message), run_time=2)
        self.wait(1)
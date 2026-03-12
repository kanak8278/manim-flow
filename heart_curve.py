from manim import *
import numpy as np

class HeartCurveComplete(Scene):
    def construct(self):
        # Set black background
        self.camera.background_color = BLACK
        
        # ==================== ACT 1: THE HOOK (0:00 - 0:30) ====================
        
        # Opening mystery questions
        question1 = Text("What is the shape of love?", font_size=36, color=WHITE)
        question1.move_to(ORIGIN)
        
        self.play(Write(question1), run_time=1.5)
        self.wait(1.5)
        
        # Transform to second question
        question2 = Text("Can mathematics capture emotion?", font_size=36)
        question2.set_color_by_gradient(WHITE, PINK)
        question2.move_to(ORIGIN)
        
        self.play(Transform(question1, question2), run_time=1.5)
        self.wait(1.5)
        
        # Fade to discovery text
        discovery = Text("Let's discover...", font_size=32, color=YELLOW)
        discovery.move_to(ORIGIN)
        
        self.play(FadeOut(question1), run_time=1)
        self.play(Write(discovery), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(discovery), run_time=0.5)
        
        # Preview: Show final heart pulsing
        def heart_preview(t):
            x = 16 * np.sin(t) ** 3
            y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            return np.array([x, y, 0])
        
        preview_heart = ParametricFunction(
            heart_preview,
            t_range=[0, 2*PI, 0.01],
            stroke_width=6,
            color=RED
        ).scale(0.15)
        preview_heart.set_fill(RED, opacity=0.3)
        
        self.play(Create(preview_heart), run_time=2)
        
        # Pulsing effect
        for _ in range(3):
            self.play(
                preview_heart.animate.scale(1.15),
                run_time=0.4,
                rate_func=smooth
            )
            self.play(
                preview_heart.animate.scale(1/1.15),
                run_time=0.4,
                rate_func=smooth
            )
        
        self.wait(0.5)
        
        # Heart explodes into equation particles and reforms
        self.play(FadeOut(preview_heart), run_time=1)
        
        # Main title appears
        main_title = Text("The Mathematical Heart", font_size=56, weight=BOLD)
        main_title.set_color_by_gradient(RED, PINK, PURPLE)
        main_title.move_to(ORIGIN)
        
        self.play(Write(main_title), run_time=2.5)
        self.wait(2)
        self.play(FadeOut(main_title), run_time=1)
        
        # ==================== ACT 2: MATHEMATICAL FOUNDATION (0:30 - 1:30) ====================
        
        # Show implicit equation with character-by-character typing
        implicit_eq_text = "(x² + y² - 1)³ = x²y³"
        implicit_eq = Text(implicit_eq_text, font_size=40)
        implicit_eq.move_to(UP * 1)
        
        # Build equation character by character with highlights
        temp_eq = Text("", font_size=40)
        temp_eq.move_to(UP * 1)
        self.add(temp_eq)
        
        for i, char in enumerate(implicit_eq_text):
            new_text = implicit_eq_text[:i+1]
            new_eq = Text(new_text, font_size=40)
            new_eq.move_to(UP * 1)
            
            # Highlight specific terms
            if "x²" in new_text and len(new_text) >= 2:
                if new_text.count("x²") == 1:
                    new_eq[0:2].set_color(BLUE)
                else:
                    new_eq[0:2].set_color(BLUE)
                    # Find second x² and color it
                    second_x = new_text.rfind("x²")
                    if second_x != -1:
                        new_eq[second_x:second_x+2].set_color(BLUE)
            if "y²" in new_text:
                y_pos = new_text.find("y²")
                if y_pos != -1:
                    new_eq[y_pos:y_pos+2].set_color(GREEN)
            if "y³" in new_text:
                y3_pos = new_text.find("y³")
                if y3_pos != -1:
                    new_eq[y3_pos:y3_pos+2].set_color(RED)
            
            self.play(Transform(temp_eq, new_eq), run_time=0.08)
        
        self.wait(1)
        
        # Explanation of complexity
        complexity_text = Text("Beautiful but implicit - hard to draw directly", 
                              font_size=24, color=YELLOW)
        complexity_text.move_to(DOWN * 0.5)
        
        self.play(Write(complexity_text), run_time=1.5)
        self.wait(1.5)
        
        # Transform to parametric form
        param_title = Text("Parametric Representation:", font_size=32, color=BLUE)
        param_title.move_to(UP * 2.5)
        
        x_param = Text("x = 16sin³(t)", font_size=28, color=WHITE)
        x_param.move_to(UP * 1.5)
        
        y_param = Text("y = 13cos(t) - 5cos(2t) - 2cos(3t) - cos(4t)", font_size=28, color=WHITE)
        y_param.move_to(UP * 0.5)
        
        t_range = Text("t ∈ [0, 2π]", font_size=24, color=GRAY)
        t_range.move_to(DOWN * 0.5)
        
        self.play(
            FadeOut(temp_eq),
            FadeOut(complexity_text),
            run_time=1
        )
        
        self.play(Write(param_title), run_time=1)
        self.play(
            Write(x_param),
            Write(y_param),
            Write(t_range),
            run_time=2.5
        )
        
        # Brief parametric explanation with rotating circle
        param_circle = Circle(radius=0.5, color=BLUE, stroke_width=2)
        param_circle.move_to(DOWN * 2 + LEFT * 4)
        param_dot = Dot(color=YELLOW).move_to(param_circle.get_start())
        
        param_label = Text("t", font_size=16, color=YELLOW)
        param_label.next_to(param_dot, RIGHT)
        
        self.play(
            Create(param_circle),
            Create(param_dot),
            Write(param_label),
            run_time=1
        )
        
        # Animate parameter rotation
        self.play(
            MoveAlongPath(param_dot, param_circle),
            Rotate(param_label, 2*PI, about_point=param_circle.get_center()),
            run_time=2,
            rate_func=linear
        )
        
        self.wait(1)
        
        # Clear parametric explanation
        self.play(
            FadeOut(param_title),
            FadeOut(x_param),
            FadeOut(y_param),
            FadeOut(t_range),
            FadeOut(param_circle),
            FadeOut(param_dot),
            FadeOut(param_label),
            run_time=1.5
        )
        
        # ==================== ACT 3: COMPONENT BUILDING (1:30 - 4:30) ====================
        
        # Setup axes - adjusted for better heart centering
        axes = Axes(
            x_range=[-25, 25, 5],
            y_range=[-20, 20, 5],
            x_length=10,
            y_length=7,
            axis_config={"stroke_width": 2, "stroke_opacity": 0.3}
        ).move_to(DOWN * 0.5)
        
        # Add subtle grid
        grid = NumberPlane(
            x_range=[-25, 25, 5],
            y_range=[-20, 20, 5],
            x_length=10,
            y_length=7,
            background_line_style={"stroke_opacity": 0.1, "stroke_width": 1}
        ).move_to(DOWN * 0.5)
        
        self.play(
            Create(grid),
            Create(axes),
            run_time=1.5
        )
        
        # Component functions
        def x_component(t):
            return 16 * np.sin(t) ** 3
        
        def y_component_1(t):
            return 13 * np.cos(t)
        
        def y_component_2(t):
            return -5 * np.cos(2 * t)
        
        def y_component_3(t):
            return -2 * np.cos(3 * t)
        
        def y_component_4(t):
            return -np.cos(4 * t)
        
        def heart_function(t, comp1=True, comp2=False, comp3=False, comp4=False):
            x = x_component(t)
            y = y_component_1(t) if comp1 else 0
            if comp2: y += y_component_2(t)
            if comp3: y += y_component_3(t)
            if comp4: y += y_component_4(t)
            return np.array([x, y, 0])
        
        # Component 1: X Foundation + Base Y
        comp1_title = Text("X Foundation: x = 16sin³(t)", font_size=32, weight=BOLD, color=GREEN)
        comp1_title.move_to(UP * 3.2)
        
        comp1_desc = Text("The heartbeat - main vertical rhythm", font_size=20, color=WHITE)
        comp1_desc.move_to(UP * 2.8)
        
        self.play(Write(comp1_title), run_time=1.5)
        self.play(Write(comp1_desc), run_time=1.5)
        
        # Highlight x equation
        x_highlight = Text("x = 16sin³(t)", font_size=24, color=GREEN)
        x_highlight.move_to(UP * 2.3)
        self.play(Write(x_highlight), run_time=1)
        
        # Draw first component (basic oval) - better positioned and scaled
        curve1 = ParametricFunction(
            lambda t: heart_function(t, comp1=True),
            t_range=[0, 4*PI, 0.01],
            stroke_width=4
        ).scale(0.15).move_to(DOWN * 0.5)
        curve1.set_color_by_gradient(GREEN, BLUE)
        
        self.play(Create(curve1), run_time=4, rate_func=linear)
        self.wait(2)
        
        # Clear component 1 text
        self.play(
            FadeOut(comp1_title),
            FadeOut(comp1_desc),
            FadeOut(x_highlight),
            run_time=1
        )
        
        # Component 2: Double Frequency
        comp2_title = Text("Adding Double Frequency: -5cos(2t)", font_size=30, weight=BOLD, color=BLUE)
        comp2_title.move_to(UP * 3.2)
        
        comp2_desc = Text("The indent begins - love takes shape", font_size=20, color=WHITE)
        comp2_desc.move_to(UP * 2.8)
        
        # Highlight the -5cos(2t) term
        y2_highlight = Text("-5cos(2t)", font_size=24, color=ORANGE)
        y2_highlight.move_to(UP * 2.3)
        y2_highlight.set_color(ORANGE)
        
        self.play(Write(comp2_title), run_time=1.5)
        self.play(Write(comp2_desc), run_time=1.5)
        self.play(Write(y2_highlight), run_time=1)
        
        # Transform to include second component
        curve2 = ParametricFunction(
            lambda t: heart_function(t, comp1=True, comp2=True),
            t_range=[0, 4*PI, 0.01],
            stroke_width=4
        ).scale(0.15).move_to(DOWN * 0.5)
        curve2.set_color_by_gradient(BLUE, PURPLE)
        
        self.play(Transform(curve1, curve2), run_time=4, rate_func=smooth)
        self.wait(2)
        
        # Clear component 2 text
        self.play(
            FadeOut(comp2_title),
            FadeOut(comp2_desc),
            FadeOut(y2_highlight),
            run_time=1
        )
        
        # Component 3: Triple Harmonics
        comp3_title = Text("Adding Triple Harmonics: -2cos(3t)", font_size=30, weight=BOLD, color=PURPLE)
        comp3_title.move_to(UP * 3.2)
        
        comp3_desc = Text("Adding character and asymmetry", font_size=20, color=WHITE)
        comp3_desc.move_to(UP * 2.8)
        
        y3_highlight = Text("-2cos(3t)", font_size=24, color=PURPLE)
        y3_highlight.move_to(UP * 2.3)
        
        self.play(Write(comp3_title), run_time=1.5)
        self.play(Write(comp3_desc), run_time=1.5)
        self.play(Write(y3_highlight), run_time=1)
        
        # Show frequency comparison
        freq_demo = VGroup(
            Text("f", font_size=16, color=GREEN),
            Text("2f", font_size=16, color=BLUE),
            Text("3f", font_size=16, color=PURPLE)
        ).arrange(RIGHT, buff=0.5)
        freq_demo.move_to(DOWN * 3)
        self.play(Write(freq_demo), run_time=1)
        
        # Transform to include third component
        curve3 = ParametricFunction(
            lambda t: heart_function(t, comp1=True, comp2=True, comp3=True),
            t_range=[0, 4*PI, 0.01],
            stroke_width=4
        ).scale(0.15).move_to(DOWN * 0.5)
        curve3.set_color_by_gradient(PURPLE, PINK)
        
        self.play(Transform(curve1, curve3), run_time=4, rate_func=smooth)
        self.wait(2)
        
        # Clear component 3 text
        self.play(
            FadeOut(comp3_title),
            FadeOut(comp3_desc),
            FadeOut(y3_highlight),
            FadeOut(freq_demo),
            run_time=1
        )
        
        # Component 4: Final Refinement
        comp4_title = Text("Final Refinement: -cos(4t)", font_size=30, weight=BOLD, color=RED)
        comp4_title.move_to(UP * 3.2)
        
        comp4_desc = Text("Mathematical perfection achieved", font_size=20, color=WHITE)
        comp4_desc.move_to(UP * 2.8)
        
        y4_highlight = Text("-cos(4t)", font_size=24, color=GOLD)
        y4_highlight.move_to(UP * 2.3)
        
        self.play(Write(comp4_title), run_time=1.5)
        self.play(Write(comp4_desc), run_time=1.5)
        self.play(Write(y4_highlight), run_time=1)
        
        # Final heart transformation
        final_heart = ParametricFunction(
            lambda t: heart_function(t, comp1=True, comp2=True, comp3=True, comp4=True),
            t_range=[0, 4*PI, 0.01],
            stroke_width=5
        ).scale(0.15).move_to(DOWN * 0.5)
        final_heart.set_color_by_gradient(RED, PINK, PURPLE, RED)
        
        self.play(Transform(curve1, final_heart), run_time=5, rate_func=smooth)
        self.wait(2)
        
        # Clear all component text and axes for finale
        self.play(
            FadeOut(comp4_title),
            FadeOut(comp4_desc),
            FadeOut(y4_highlight),
            FadeOut(axes),
            FadeOut(grid),
            run_time=1.5
        )
        
        # ==================== ACT 4: MATHEMATICAL ANALYSIS (4:30 - 5:30) ====================
        
        # Scale up the heart for analysis - better positioning
        self.play(
            curve1.animate.scale(4).move_to(UP * 0.3),
            run_time=2
        )
        
        # Show decomposition with mini hearts - repositioned
        mini_hearts = []
        positions = [UP*1+LEFT*4, UP*1+LEFT*2, UP*1+RIGHT*2, UP*1+RIGHT*4, DOWN*2.5]
        labels = ["Base", "+2f", "+3f", "+4f", "Complete"]
        colors = [GREEN, BLUE, PURPLE, YELLOW, RED]
        
        for i, (pos, label, color) in enumerate(zip(positions, labels, colors)):
            mini_heart = ParametricFunction(
                lambda t: heart_function(t, 
                                       comp1=True, 
                                       comp2=i>=1, 
                                       comp3=i>=2, 
                                       comp4=i>=3),
                t_range=[0, 2*PI, 0.02],
                stroke_width=2,
                color=color
            ).scale(0.08).move_to(pos)
            
            label_text = Text(label, font_size=12, color=color)
            label_text.move_to(pos + DOWN*0.6)
            
            mini_hearts.append(VGroup(mini_heart, label_text))
        
        analysis_title = Text("Component Analysis", font_size=36, weight=BOLD, color=YELLOW)
        analysis_title.move_to(UP*3.5)
        
        self.play(Write(analysis_title), run_time=1)
        
        for mini_heart_group in mini_hearts:
            self.play(Create(mini_heart_group), run_time=0.5)
        
        self.wait(3)
        
        # Clear analysis
        self.play(
            FadeOut(analysis_title),
            *[FadeOut(mh) for mh in mini_hearts],
            run_time=1
        )
        
        # ==================== ACT 5: GRAND FINALE (5:30 - 6:30) ====================
        
        # Rainbow heart rebuild
        finale_title = Text("The Complete Mathematical Heart", font_size=42, weight=BOLD)
        finale_title.set_color_by_gradient(RED, PINK, PURPLE)
        finale_title.move_to(UP*3.5)
        
        self.play(Write(finale_title), run_time=2)
        
        # Clear existing heart
        self.play(FadeOut(curve1), run_time=1)
        
        # Create a centered heart to fill the empty space
        center_heart = ParametricFunction(
            lambda t: heart_function(t, comp1=True, comp2=True, comp3=True, comp4=True),
            t_range=[0, 2*PI, 0.01],
            stroke_width=4,
            color=RED
        ).scale(0.4).move_to(UP * 0.3)
        center_heart.set_fill(RED, opacity=0.2)
        
        self.play(Create(center_heart), run_time=2)
        self.wait(1)
        
        # Clear center heart and build rainbow segments
        self.play(FadeOut(center_heart), run_time=0.5)
        
        # Build rainbow heart with 12 segments
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, RED, ORANGE, YELLOW, GREEN, BLUE]
        segments = []
        
        for i, color in enumerate(colors):
            segment = ParametricFunction(
                lambda t: heart_function(t, comp1=True, comp2=True, comp3=True, comp4=True),
                t_range=[i*2*PI/12, (i+1)*2*PI/12, 0.01],
                stroke_width=6,
                color=color
            ).scale(0.6).move_to(UP * 0.3)
            segments.append(segment)
        
        # Draw segments progressively
        rainbow_heart = VGroup()
        for segment in segments:
            rainbow_heart.add(segment)
            self.play(Create(segment), run_time=0.3, rate_func=linear)
        
        self.wait(1)
        
        # Heartbeat animation (3 double beats)
        for beat in range(3):
            # Lub
            self.play(
                rainbow_heart.animate.scale(1.1),
                run_time=0.2,
                rate_func=smooth
            )
            self.play(
                rainbow_heart.animate.scale(1/1.1),
                run_time=0.3,
                rate_func=smooth
            )
            # Dub
            self.play(
                rainbow_heart.animate.scale(1.05),
                run_time=0.15,
                rate_func=smooth
            )
            self.play(
                rainbow_heart.animate.scale(1/1.05),
                run_time=0.25,
                rate_func=smooth
            )
            self.wait(0.6)  # Pause between beats
        
        # 3D revolution effect
        self.play(
            Rotate(rainbow_heart, angle=2*PI, axis=UP),
            run_time=4,
            rate_func=smooth
        )
        
        # Final messages
        message1 = Text("Love is complex...", font_size=24, color=WHITE)
        message1.move_to(DOWN*2.5 + LEFT*3)
        
        message2 = Text("Love has many frequencies...", font_size=24, color=WHITE)
        message2.move_to(DOWN*2.5 + RIGHT*3)
        
        message3 = Text("But with mathematics...", font_size=28, color=YELLOW)
        message3.move_to(DOWN*1.5)
        
        message4 = Text("We can understand its perfect form", font_size=32, weight=BOLD, color=PINK)
        message4.move_to(DOWN*0.8)
        
        self.play(Write(message1), run_time=1)
        self.wait(0.5)
        self.play(Write(message2), run_time=1)
        self.wait(0.5)
        self.play(Write(message3), run_time=1.5)
        self.wait(0.5)
        self.play(Write(message4), run_time=1.5)
        self.wait(2)
        
        # Final equation with heart emoji properly positioned
        math_text = Text("Mathematics + Art = ", font_size=36, weight=BOLD, color=WHITE)
        heart_emoji = Text("❤️", font_size=48)
        heart_emoji.set_color(RED)
        
        final_message = VGroup(math_text, heart_emoji).arrange(RIGHT, buff=0.2)
        final_message.set_color_by_gradient(RED, PINK)
        final_message.move_to(DOWN*2)
        
        self.play(
            FadeOut(message1),
            FadeOut(message2),
            FadeOut(message3),
            FadeOut(message4),
            Write(final_message),
            run_time=2
        )
        
        # Final heart pulse and fade
        self.play(
            rainbow_heart.animate.scale(1.2),
            run_time=1,
            rate_func=smooth
        )
        
        self.wait(2)
        
        # Everything fades to black
        everything = Group(finale_title, rainbow_heart, final_message)
        self.play(FadeOut(everything), run_time=3)
        
        self.wait(1)

# ManimFlow - Complete Mathematical Heart Animation with Detailed Script
# To render: uv run python -m manim -pqh heart_curve.py HeartCurveComplete
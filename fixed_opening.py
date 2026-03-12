from manim import *
import numpy as np

class FixedOpeningScene(Scene):
    def construct(self):
        # Set sky gradient background
        self.camera.background_color = "#87CEEB"
        
        # Constants for projectile motion
        angle = 30 * DEGREES
        initial_speed = 20  # m/s
        g = 10  # m/s^2
        
        # Calculate projectile parameters
        v_x = initial_speed * np.cos(angle)
        v_y = initial_speed * np.sin(angle)
        time_to_peak = v_y / g
        max_height = v_y**2 / (2 * g)
        
        # [0-2s] CINEMATIC HOOK - Ball at peak with drama
        ball = Circle(radius=0.3, fill_opacity=1, fill_color=ORANGE, stroke_width=3, stroke_color=YELLOW)
        ball.move_to(UP * 2.5)  # Start at peak height
        
        # Particle glow effect around ball
        glow_particles = VGroup()
        for i in range(12):
            particle = Dot(radius=0.05, color=YELLOW)
            angle_offset = i * TAU / 12
            particle.move_to(ball.get_center() + 0.6 * np.array([np.cos(angle_offset), np.sin(angle_offset), 0]))
            glow_particles.add(particle)
        
        # Initial dramatic setup
        self.add(ball, glow_particles)
        
        # Pulsing glow effect
        self.play(
            glow_particles.animate.scale(1.3).set_opacity(0.7),
            ball.animate.scale(1.1),
            run_time=0.5
        )
        self.play(
            glow_particles.animate.scale(1/1.3).set_opacity(0.5),
            ball.animate.scale(1/1.1),
            run_time=0.5
        )
        
        # "HOW HIGH?" text appears dramatically
        how_high_text = Text("HOW HIGH?", font_size=84, weight=BOLD)
        how_high_text.set_color_by_gradient(BLUE, TEAL)
        how_high_text.move_to(UP * 0.5)
        how_high_text.scale(0)
        
        self.play(
            how_high_text.animate.scale(1.2),
            run_time=0.8,
            rate_func=smooth
        )
        self.play(how_high_text.animate.scale(1/1.2), run_time=0.2)
        
        # [2-4s] PROBLEM REVEAL
        self.play(
            FadeOut(how_high_text),
            FadeOut(glow_particles),
            run_time=0.5
        )
        
        # Create ground line
        ground = Line(LEFT * 6, RIGHT * 6, stroke_width=4, color=GREEN)
        ground.move_to(DOWN * 3)
        self.add(ground)
        
        # Create stick figure thrower
        head = Circle(radius=0.15, fill_opacity=1, fill_color=PINK, stroke_width=2)
        body = Line(ORIGIN, DOWN * 0.8, stroke_width=4)
        left_arm = Line(ORIGIN, LEFT * 0.4 + DOWN * 0.2, stroke_width=3)
        right_arm = Line(ORIGIN, RIGHT * 0.5 + UP * 0.3, stroke_width=3)  # Throwing arm
        left_leg = Line(DOWN * 0.8, LEFT * 0.3 + DOWN * 1.2, stroke_width=3)
        right_leg = Line(DOWN * 0.8, RIGHT * 0.3 + DOWN * 1.2, stroke_width=3)
        
        stick_figure = VGroup(head, body, left_arm, right_arm, left_leg, right_leg)
        stick_figure.set_color(DARK_BLUE)
        stick_figure.move_to(LEFT * 4 + DOWN * 2.1)
        
        # Move ball to thrower's hand
        ball.move_to(stick_figure[3].get_end())  # Right arm end
        
        self.play(FadeIn(stick_figure), ball.animate.move_to(stick_figure[3].get_end()), run_time=0.5)
        
        # Show angle indicator
        angle_arc = Arc(
            radius=0.8,
            start_angle=0,
            angle=angle,
            arc_center=stick_figure.get_center() + UP * 0.5,
            stroke_width=4,
            color=RED
        )
        
        angle_label = Text("30°", color=RED, font_size=36)
        angle_label.next_to(angle_arc, RIGHT * 0.5)
        
        self.play(Create(angle_arc), Write(angle_label), run_time=0.8)
        
        # Show speed indicator
        speed_arrow = Arrow(
            stick_figure[3].get_end(),
            stick_figure[3].get_end() + 2 * np.array([np.cos(angle), np.sin(angle), 0]),
            stroke_width=6,
            color=BLUE,
            buff=0
        )
        
        speed_label = Text("20 m/s", color=BLUE, font_size=32, weight=BOLD)
        speed_label.next_to(speed_arrow.get_end(), UP)
        
        self.play(Create(speed_arrow), Write(speed_label), run_time=0.8)
        
        # Show trajectory preview as dotted line
        trajectory_points = []
        for t in np.linspace(0, 2 * time_to_peak, 50):
            x = v_x * t
            y = v_y * t - 0.5 * g * t**2
            if y >= 0:  # Only show above ground
                trajectory_points.append(stick_figure.get_center() + UP * 0.5 + np.array([x, y, 0]))
        
        trajectory = VMobject()
        trajectory.set_points_as_corners(trajectory_points)
        trajectory.set_stroke(YELLOW, width=4, opacity=0.8)
        trajectory.set_fill(opacity=0)
        
        # Make it dotted
        trajectory.set_stroke(YELLOW, width=4)
        trajectory_dashed = DashedVMobject(trajectory, num_dashes=30, dashed_ratio=0.6)
        
        self.play(Create(trajectory_dashed), run_time=1.0)
        
        # "The Challenge" text
        challenge_text = Text("The Challenge", font_size=48, weight=BOLD, color=DARK_BLUE)
        challenge_text.move_to(UP * 3)
        self.play(Write(challenge_text), run_time=0.5)
        
        # [4-6s] PHYSICS PREVIEW
        self.wait(0.3)
        self.play(FadeOut(challenge_text), run_time=0.3)
        
        # Move ball to launch position
        ball.move_to(stick_figure.get_center() + UP * 0.5)
        
        # Main velocity vector (update existing speed_arrow)
        main_vector = Arrow(
            ball.get_center(),
            ball.get_center() + 1.5 * np.array([np.cos(angle), np.sin(angle), 0]),
            stroke_width=6,
            color=BLUE,
            buff=0
        )
        
        self.play(
            ball.animate.move_to(stick_figure.get_center() + UP * 0.5),
            Transform(speed_arrow, main_vector),
            speed_label.animate.move_to(main_vector.get_end() + UP * 0.3),
            run_time=0.8
        )
        
        # Split into components - create new arrows
        v_x_arrow = Arrow(
            ball.get_center(),
            ball.get_center() + 1.3 * RIGHT,
            stroke_width=5,
            color=GREEN,
            buff=0
        )
        
        v_y_arrow = Arrow(
            ball.get_center(),
            ball.get_center() + 1.0 * UP,
            stroke_width=5,
            color=PURPLE,
            buff=0
        )
        
        v_x_label = Text("17.3 m/s", color=GREEN, font_size=28)
        v_x_label.next_to(v_x_arrow, DOWN)
        
        v_y_label = Text("10 m/s", color=PURPLE, font_size=28, weight=BOLD)
        v_y_label.next_to(v_y_arrow, RIGHT)
        
        self.play(
            Create(v_x_arrow),
            Create(v_y_arrow),
            Write(v_x_label),
            Write(v_y_label),
            run_time=1.0
        )
        
        # Gravity arrow
        gravity_arrow = Arrow(
            ball.get_center() + UP * 0.8,
            ball.get_center() + UP * 0.2,
            stroke_width=6,
            color=RED,
            buff=0
        )
        gravity_label = Text("g = 10 m/s²", color=RED, font_size=28)
        gravity_label.next_to(gravity_arrow, RIGHT)
        
        self.play(Create(gravity_arrow), Write(gravity_label), run_time=0.8)
        
        # Show ball reaching peak
        peak_point = trajectory_points[len(trajectory_points)//2] if trajectory_points else UP * 2
        
        self.play(
            ball.animate.move_to(peak_point),
            v_y_arrow.animate.scale(0.1).set_opacity(0.3),
            run_time=0.8
        )
        
        # "v = 0" at peak
        zero_velocity = Text("v = 0", color=RED, font_size=36, weight=BOLD)
        zero_velocity.next_to(ball, UP)
        self.play(Write(zero_velocity), run_time=0.5)
        
        # "Physics Made Simple!" text
        physics_text = Text("Physics Made Simple!", font_size=48, weight=BOLD)
        physics_text.set_color_by_gradient(BLUE, GREEN)
        physics_text.move_to(DOWN * 0.5)
        
        self.play(Write(physics_text), run_time=0.8)
        
        # [6-8s] TITLE CARD & SETUP
        self.wait(0.5)
        
        # Clear everything for clean title
        all_objects = VGroup(
            ball, stick_figure, angle_arc, angle_label, speed_arrow, speed_label,
            trajectory_dashed, v_x_arrow, v_y_arrow, v_x_label, v_y_label,
            gravity_arrow, gravity_label, zero_velocity, physics_text, ground
        )
        self.play(FadeOut(all_objects), run_time=0.8)
        
        # Final title card
        main_title = Text("HOW HIGH CAN YOU THROW?", font_size=64, weight=BOLD)
        main_title.set_color_by_gradient(BLUE, TEAL, GREEN)
        
        subtitle = Text("Physics Made Simple!", font_size=36)
        subtitle.set_color(DARK_BLUE)
        subtitle.next_to(main_title, DOWN, buff=0.5)
        
        # Physics icons around title
        ball_icon = Circle(radius=0.2, fill_opacity=1, fill_color=ORANGE, stroke_width=2)
        ball_icon.move_to(LEFT * 4 + UP * 1)
        
        arrow_icon = Arrow(LEFT * 0.3, RIGHT * 0.3, stroke_width=4, color=BLUE)
        arrow_icon.move_to(RIGHT * 4 + UP * 1)
        
        formula_icon = Text("h = v²/2g", color=GREEN, font_size=32)
        formula_icon.move_to(DOWN * 2)
        
        title_group = VGroup(main_title, subtitle, ball_icon, arrow_icon, formula_icon)
        
        self.play(
            Write(main_title),
            Write(subtitle),
            FadeIn(ball_icon),
            Create(arrow_icon),
            Write(formula_icon),
            run_time=1.5
        )
        
        # Hold and fade for transition
        self.wait(0.5)
        self.play(FadeOut(title_group), run_time=0.5)

# ManimFlow - Fixed Opening Scene for Projectile Physics
# To render: uv run manim -pqh fixed_opening.py FixedOpeningScene
import tkinter as tk
from tkinter import ttk, messagebox
import time

from models import RoomType, ActorType, EquipmentState
from simulation import HospitalSimulation
from metrics import ActivityLogger, MetricsTracker, PerformanceAnalyzer

class HospitalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Hospital Predictive System - Time & Energy Optimization")
        self.root.geometry("1500x950")
        
        # Initialize components
        self.simulation = HospitalSimulation()
        self.activity_logger = ActivityLogger()
        self.metrics_tracker = MetricsTracker()
        self.performance_analyzer = PerformanceAnalyzer(self.metrics_tracker)
        
        self.canvas_width = 900
        self.canvas_height = 400
        
        self.selected_actor = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.running = True
        self.setup_gui()
        
        self.schedule_updates()
        
    def setup_gui(self):
        """Setup the complete GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Project header
        header_frame = ttk.Frame(control_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="Smart Hospital\nPredictive System", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Time & Energy Optimization Demo", 
                                  font=("Arial", 10), foreground="blue")
        subtitle_label.pack()
        
        # Mode Selection
        mode_frame = ttk.LabelFrame(control_frame, text="🎯 Operation Mode")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.BooleanVar(value=True)
        self.predictive_radio = ttk.Radiobutton(mode_frame, text="🔮 Predictive Mode", 
                                               variable=self.mode_var, value=True,
                                               command=self.toggle_mode)
        self.predictive_radio.pack(anchor='w')
        
        self.non_predictive_radio = ttk.Radiobutton(mode_frame, text="⏰ Traditional Mode", 
                                                   variable=self.mode_var, value=False,
                                                   command=self.toggle_mode)
        self.non_predictive_radio.pack(anchor='w')
        
        # Mode description
        self.mode_desc = ttk.Label(mode_frame, text="Equipment preloading based on movement patterns", 
                                  font=("Arial", 9), foreground="green", width=30)
        self.mode_desc.pack(anchor='w', pady=(5,0))
        
        # Simulation Control
        sim_frame = ttk.LabelFrame(control_frame, text="🎮 Simulation Control")
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(sim_frame, text="🎮 Manual Mode (Drag & Drop)", 
                  command=self.start_manual_mode).pack(fill=tk.X, pady=1)
        ttk.Button(sim_frame, text="🤖 Auto Demo (Realistic)", 
                  command=self.pick_simulation).pack(fill=tk.X, pady=1)
        ttk.Button(sim_frame, text="⏹️ Stop Auto Demo", 
                  command=self.stop_auto_simulation).pack(fill=tk.X, pady=1)
        
        # Hospital Workflow Info
        workflow_frame = ttk.LabelFrame(control_frame, text="🏥 Hospital Workflow")
        workflow_frame.pack(fill=tk.X, pady=(0, 10))
        
        workflow_steps = [
            "1. Staff enters → Equipment starts",
            "2. Doctor enters → Waits for ready",
            "3. Patient enters → Examination begins",
            "4. Idle 10s → Sleep mode (10% power)",
            "5. Empty 30s → Equipment shuts down"
        ]
        for step in workflow_steps:
            ttk.Label(workflow_frame, text=step, font=("Arial", 8)).pack(anchor='w')
        
        # Actor Management
        actor_frame = ttk.LabelFrame(control_frame, text="👥 Manage Actors")
        actor_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(actor_frame, text="Add Doctor (Green)", 
                  command=lambda: self.add_actor(ActorType.DOCTOR)).pack(fill=tk.X, pady=1)
        ttk.Button(actor_frame, text="Add Staff (Blue)", 
                  command=lambda: self.add_actor(ActorType.STAFF)).pack(fill=tk.X, pady=1)
        ttk.Button(actor_frame, text="Add Patient (Red)", 
                  command=lambda: self.add_actor(ActorType.PATIENT)).pack(fill=tk.X, pady=1)
        ttk.Button(actor_frame, text="Remove Selected Actor", 
                  command=self.remove_selected_actor).pack(fill=tk.X, pady=1)
        
        # Performance Metrics
        performance_frame = ttk.LabelFrame(control_frame, text="📊 Performance Metrics")
        performance_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.performance_metrics = {}
        performance_labels = [
            'Total Tasks', 'Examinations Done', 'Prediction Accuracy',
            'Time Saved (s)', 'Time Lost (s)', 'Net Time Benefit (s)',
            'Current Power (kW)', 'Total Power (kW)' ,'Energy Saved (kWh)'
        ]
        for metric in performance_labels:
            label = ttk.Label(performance_frame, text=f"{metric}: 0", font=("Arial", 8))
            label.pack(anchor='w')
            self.performance_metrics[metric] = label
        
        # Control Buttons
        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_buttons_frame, text="Reset System", 
                  command=self.reset_simulation).pack(fill=tk.X, pady=2)
        ttk.Button(control_buttons_frame, text="Performance Report", 
                  command=self.show_performance_report).pack(fill=tk.X, pady=2)
        ttk.Button(control_buttons_frame, text="Export Metrics", 
                  command=self.export_metrics).pack(fill=tk.X, pady=2)
        
        # Legend
        legend_frame = ttk.LabelFrame(control_frame, text="Legend")
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_items = [
            "Staff (Blue) - RFID: S001",
            "Doctor (Green) - RFID: D001", 
            "Patient (Red) - RFID: P001",
            "Sleep Mode = 10% Power",
            "Drag & Drop to Move",
            "Watch time/energy savings!"
        ]
        for item in legend_items:
            ttk.Label(legend_frame, text=item, font=("Arial", 8)).pack(anchor='w')
        
        # Right panel for visualization
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas title
        canvas_title = ttk.Label(viz_frame, text="Hospital Layout - Smart Equipment Management", 
                                font=("Arial", 12, "bold"))
        canvas_title.pack(pady=(0, 5))
        
        # Canvas for hospital layout
        self.canvas = tk.Canvas(viz_frame, width=self.canvas_width, height=self.canvas_height, 
                               bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(pady=(0, 10))
        
        # Bind mouse events for drag & drop
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_hover)
        
        # Bottom information panels
        info_frame = ttk.Frame(viz_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Equipment status panel
        equipment_frame = ttk.LabelFrame(info_frame, text="Real-time Equipment Status")
        equipment_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.equipment_text = tk.Text(equipment_frame, height=14, width=40, font=("Consolas", 9))
        eq_scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_text.yview)
        self.equipment_text.configure(yscrollcommand=eq_scrollbar.set)
        self.equipment_text.pack(side="left", fill="both", expand=True)
        eq_scrollbar.pack(side="right", fill="y")
        
        # Activity log panel
        activity_frame = ttk.LabelFrame(info_frame, text="Hospital Activity Log")
        activity_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.activity_text = tk.Text(activity_frame, height=14, width=40, font=("Consolas", 9))
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=activity_scrollbar.set)
        self.activity_text.pack(side="left", fill="both", expand=True)
        activity_scrollbar.pack(side="right", fill="y")
        
        # Initialize display
        self.draw_hospital_layout()
        
        # Add initial actors for demo
        self.add_actor(ActorType.STAFF)
        self.add_actor(ActorType.DOCTOR)
        self.add_actor(ActorType.PATIENT)
        
        # Force initial display
        self.update_display()
        self.root.after(500, self.update_display)
        
    def schedule_updates(self):
        """Schedule all update loops for real-time simulation"""
        if self.running:
            self.equipment_update()
            self.room_update()
            self.update_display()
            self.update_all_metrics()
            self.root.after(1000, self.schedule_updates)
    
    def toggle_mode(self):
        """Toggle between predictive and traditional mode"""
        predictive = self.mode_var.get()
        self.simulation.set_predictive_mode(predictive)
        
        if predictive:
            self.mode_desc.config(text="Equipment preloading based on movement patterns", foreground="green")
            mode_msg = "PREDICTIVE MODE: Equipment preloading enabled"
        else:
            self.mode_desc.config(text="Manual equipment activation only", foreground="red")
            mode_msg = "TRADITIONAL MODE: Manual equipment startup only"
        
        self.log_activity(mode_msg)
    
    def start_manual_mode(self):
        """Enable manual drag & drop control"""
        self.simulation.auto_simulation_running = False
        self.log_activity("MANUAL MODE: Drag actors between rooms")
    def pick_simulation(self):
        if self.mode_var.get()==False:
            self.start_auto_simulation()
        else:
            self.simulation.auto_simulation_running = True
            self.auto_simulation_predictive_loop()
    def start_auto_simulation(self):
        """Start realistic automated hospital workflow demo"""
        if not self.simulation.actors:
            messagebox.showwarning("Warning", "Please add actors first!")
            return
        self.simulation.auto_simulation_running = True
        self.log_activity("AUTO DEMO: Realistic hospital workflow started")
        self.auto_simulation_loop()

    def auto_simulation_predictive_loop(self):
        """Run the predictive auto demo with preloading logic."""
        if self.simulation.auto_simulation_running and self.running:
            if self.simulation.auto_simulation_step_execute_predictive():
                self.root.after(1000, self.auto_simulation_predictive_loop)
            else:
                self.log_activity("AUTO DEMO: Predictive cycle complete, restarting...")
                self.root.after(5000, self.auto_simulation_predictive_loop)
    
    def stop_auto_simulation(self):
        """Stop automated simulation"""
        self.simulation.auto_simulation_running = False
        self.log_activity("AUTO DEMO: Simulation stopped")
    
    def auto_simulation_loop(self):
        """Run the automated demo loop"""
        if self.simulation.auto_simulation_running and self.running:
            if self.simulation.auto_simulation_step_execute():
                self.root.after(1000, self.auto_simulation_loop)
            else:
                self.log_activity("AUTO DEMO: Cycle complete, restarting...")
                self.root.after(5000, self.auto_simulation_loop)
    
    def draw_hospital_layout(self):
        """Draw the hospital layout with equipment visualization"""
        self.canvas.delete("room")
        
        rooms_layout = [
            ("Radiology", 0, 0, 300, 200, "lightgreen"),
            ("ICU", 0, 200, 300, 200, "lightcoral"),
            ("Lobby", 300, 0, 300, 200, "lightblue"),
            ("Laboratory", 300, 200, 300, 200, "lightyellow"),
            ("Patient Room", 600, 0, 300, 200, "plum1"),
            ("Emergency Room", 600, 200, 300, 200, "red")
        ]
        
        for name, x, y, w, h, color in rooms_layout:
            self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="black", 
                                       width=3, tags="room")
            
            self.canvas.create_text(x+w//2, y+15, text=f"{name}", 
                                  font=("Arial", 12, "bold"), tags="room")
            
            # Find corresponding room and draw equipment
            room_type = None
            for rt, room in self.simulation.rooms.items():
                if room.position == (x, y):
                    room_type = rt
                    break
            
            if room_type and room_type != RoomType.LOBBY:
                room = self.simulation.rooms[room_type]
                self.draw_room_equipment(room, x, y, w, h)
    
    def draw_room_equipment(self, room, x, y, w, h):
        """Draw equipment status indicators in each room"""
        equipment_per_row = 2
        eq_width = 60
        eq_height = 40
        start_x = x + 20
        start_y = y + 40
        
        for i, equipment in enumerate(room.equipment):
            row = i // equipment_per_row
            col = i % equipment_per_row
            eq_x = start_x + col * (eq_width + 20)
            eq_y = start_y + row * (eq_height + 10)
            
            # Equipment state colors
            state_colors = {
                EquipmentState.OFF: "gray",
                EquipmentState.STARTING: "orange", 
                EquipmentState.PRELOADED: "yellow",
                EquipmentState.READY: "green",
                EquipmentState.IN_USE: "blue",
                EquipmentState.SLEEP: "purple",
                EquipmentState.SHUTTING_DOWN: "red"
            }
            
            color = state_colors.get(equipment.state, "gray")
            
            # Equipment box
            self.canvas.create_rectangle(eq_x, eq_y, eq_x+eq_width, eq_y+eq_height,
                                       fill=color, outline="black", width=2, tags="room")
            
            # Equipment name
            short_name = equipment.name.split()[0][:8]
            self.canvas.create_text(eq_x + eq_width//2, eq_y + 10, text=short_name,
                                  font=("Arial", 8, "bold"), tags="room", fill="white")
            
            # State indicator
            state_text = equipment.state.value[:4]
            self.canvas.create_text(eq_x + eq_width//2, eq_y + 22, text=state_text,
                                  font=("Arial", 7), tags="room", fill="white")
            
            # Special indicators
            if equipment.state == EquipmentState.SLEEP:
                self.canvas.create_text(eq_x + eq_width//2, eq_y + 32, text="💤",
                                      font=("Arial", 10), tags="room")
            elif equipment.state in [EquipmentState.STARTING, EquipmentState.SHUTTING_DOWN]:
                progress = equipment.get_progress()
                bar_width = eq_width - 10
                bar_x = eq_x + 5
                bar_y = eq_y + eq_height - 8
                
                self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + 4,
                                           fill="white", outline="black", tags="room")
                if progress > 0:
                    fill_width = bar_width * progress
                    self.canvas.create_rectangle(bar_x, bar_y, bar_x + fill_width, bar_y + 4,
                                               fill="darkgreen", outline="", tags="room")
    
    def add_actor(self, actor_type: ActorType):
        """Add a new actor"""
        actor = self.simulation.add_actor(actor_type)
        self.log_activity(f"Added {actor_type.value} #{actor.actor_id} (Tag: {actor.tag_id})")
        self.draw_actors()
        return actor
    
    def remove_selected_actor(self):
        """Remove the currently selected actor"""
        if self.selected_actor:
            actor_info = f"{self.selected_actor.actor_type.value} #{self.selected_actor.actor_id}"
            tag_info = self.selected_actor.tag_id
            self.simulation.remove_actor(self.selected_actor)
            self.selected_actor = None
            self.log_activity(f"Removed {actor_info} (Tag: {tag_info})")
        else:
            messagebox.showinfo("Selection Required", "Please select an actor first by clicking on it.")
    
    def show_performance_report(self):
        """Show comprehensive performance report with recommendations"""
        summary = self.simulation.get_performance_summary()
        analysis = self.metrics_tracker.get_movement_analysis()
        recommendations = self.performance_analyzer.generate_recommendations(self.simulation)
        
        report = f"""
SMART HOSPITAL PERFORMANCE REPORT

SIMULATION OVERVIEW:
Runtime: {summary['runtime_minutes']:.1f} minutes
Total Tasks Completed: {summary['total_tasks']}
Medical Examinations: {summary['examinations']}
Current Mode: {'🔮 Predictive' if self.simulation.predictive_mode else '⏰ Traditional'}

TIME ANALYSIS:
Time Saved by Prediction: {summary['time_saved_total']:.1f} seconds
Time Lost to Delays: {summary['time_lost_total']:.1f} seconds
Net Time Benefit: {summary['net_time_benefit']:+.1f} seconds
Average Time per Task: {summary['avg_time_per_task']:+.1f} seconds

PREDICTION PERFORMANCE:
Prediction Accuracy: {summary['prediction_accuracy']:.1f}%
Resources Preloaded: {summary['resources_preloaded']}

ENERGY ANALYSIS:
Total Energy Consumed: {summary['energy_consumed_kwh']:.3f} kWh
Energy Saved by Sleep Mode: {summary['energy_saved_kwh']:.3f} kWh
Energy Efficiency: {summary['energy_efficiency_percent']:.1f}%

MOVEMENT ANALYSIS:
Total Movements: {analysis.get('total_movements', 0)}
Positive Outcomes: {analysis.get('positive_outcomes', 0)}
Negative Outcomes: {analysis.get('negative_outcomes', 0)}
Best Time Effect: {analysis.get('best_effect', 0):.1f}s
Worst Time Effect: {analysis.get('worst_effect', 0):.1f}s

RECOMMENDATIONS:
"""
        for rec in recommendations:
            report += f"• {rec}\n"
        
        report += f"""

🎯 PROJECT IMPACT:
{'Predictive system shows time savings!' if summary['net_time_benefit'] > 0 else 'Consider optimizing prediction algorithm'}
{'Good prediction accuracy achieved!' if summary['prediction_accuracy'] > 70 else ' Prediction accuracy needs improvement'}
{'Energy efficiency through sleep mode!' if summary['energy_efficiency_percent'] > 5 else ' Monitor energy consumption patterns'}
        """
        
        # Create popup window for report
        report_window = tk.Toplevel(self.root)
        report_window.title("Performance Report - Smart Hospital System")
        report_window.geometry("700x600")
        
        text_widget = tk.Text(report_window, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(report_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Close Report", 
                  command=report_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Export Report", 
                  command=lambda: self.export_report(report)).pack(side=tk.RIGHT, padx=(0, 5))
    
    def export_metrics(self):
        """Export metrics to file"""
        try:
            filename = f"hospital_metrics_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            result = self.metrics_tracker.export_metrics(filename)
            messagebox.showinfo("Export Successful", result)
            self.log_activity(f"Metrics exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export metrics: {e}")
    
    def export_report(self, report_content: str):
        """Export performance report to file"""
        try:
            filename = f"hospital_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report_content)
            messagebox.showinfo("Export Successful", f"Report exported to {filename}")
            self.log_activity(f"📈 Performance report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
    
    def find_actor_at_position(self, x: int, y: int):
        """Find actor at given canvas coordinates"""
        for actor in self.simulation.actors:
            if abs(x - actor.position.x) <= 15 and abs(y - actor.position.y) <= 15:
                return actor
        return None
    
    def on_click(self, event):
        """Handle mouse click for actor selection"""
        if not self.simulation.auto_simulation_running:
            actor = self.find_actor_at_position(event.x, event.y)
            if actor:
                self.selected_actor = actor
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                actor.being_dragged = True
                self.canvas.config(cursor="hand2")
                
                self.log_activity(f"👆 Selected {actor.actor_type.value} #{actor.actor_id} (Tag: {actor.tag_id})")
    
    def on_drag(self, event):
        """Handle mouse drag for actor movement"""
        if self.selected_actor and not self.simulation.auto_simulation_running:
            self.selected_actor.position.x = event.x
            self.selected_actor.position.y = event.y
            self.draw_actors()
    
    def on_release(self, event):
        """Handle mouse release to complete actor movement"""
        if self.selected_actor and not self.simulation.auto_simulation_running:
            old_room = self.selected_actor.current_room
            
            # Execute movement
            self.simulation.move_actor_to_position(self.selected_actor, event.x, event.y)
            
            # Log movement with metrics tracker
            if old_room != self.selected_actor.current_room and self.simulation.movement_log:
                movement_info = self.simulation.movement_log[-1]
                self.metrics_tracker.log_movement(movement_info)
                
                net_effect = movement_info['net_effect']
                effect_icon = "⚡" if net_effect > 0 else "🐌" if net_effect < 0 else "⚖️"
                
                self.log_activity(
                    f"{effect_icon} {self.selected_actor.actor_type.value} #{self.selected_actor.actor_id}: "
                    f"{old_room.value} → {self.selected_actor.current_room.value} "
                    f"(Net: {net_effect:+.1f}s)"
                )
            
            # Clean up selection
            self.selected_actor.being_dragged = False
            self.selected_actor = None
            self.canvas.config(cursor="")
    
    def on_hover(self, event):
        """Handle mouse hover for visual feedback"""
        if not self.selected_actor and not self.simulation.auto_simulation_running:
            actor = self.find_actor_at_position(event.x, event.y)
            self.canvas.config(cursor="hand1" if actor else "")
    
    def reset_simulation(self):
        """Reset the entire simulation"""
        self.simulation = HospitalSimulation()
        self.simulation.set_predictive_mode(self.mode_var.get())
        self.selected_actor = None
        
        # Reset metrics and logging
        self.metrics_tracker.reset_metrics()
        self.activity_logger.clear_log()
        
        # Clear displays
        self.equipment_text.delete(1.0, tk.END)
        self.activity_text.delete(1.0, tk.END)
        
        # Log reset
        self.log_activity(" === SYSTEM RESET ===")
        self.log_activity(" Smart Hospital Predictive System Ready")
        self.log_activity(" Project Demo: Time & Energy Optimization")
        
        # Add initial actors
        self.add_actor(ActorType.STAFF)
        self.add_actor(ActorType.DOCTOR) 
        self.add_actor(ActorType.PATIENT)
    
    def equipment_update(self):
        """Update all equipment states"""
        for room in self.simulation.rooms.values():
            for equipment in room.equipment:
                equipment.update_state()
        self.update_equipment_display()
    
    def room_update(self):
        """Update room states and handle examinations"""
        self.simulation.update_all_rooms()
        
        # Update energy metrics
        current_power, sleep_savings = self.simulation.calculate_energy_consumption()
        energy_consumed = current_power  # Convert to kWh for 1-second interval
        self.metrics_tracker.update_energy_metrics(energy_consumed, sleep_savings)
    
    def update_display(self):
        """Update the complete visual display"""
        self.draw_hospital_layout()
        self.draw_actors()
    
    def draw_actors(self):
        """Draw all actors with visual representation"""
        self.canvas.delete("actor")
        
        for actor in self.simulation.actors:
            x = actor.position.x
            y = actor.position.y
            
            # Ensure actors stay within canvas bounds
            x = max(15, min(self.canvas_width-15, x))
            y = max(15, min(self.canvas_height-15, y))
            actor.position.x = x
            actor.position.y = y
            
            # Actor colors
            colors = {
                ActorType.STAFF: "blue",
                ActorType.DOCTOR: "green", 
                ActorType.PATIENT: "red"
            }
            color = colors[actor.actor_type]
            
            # Special highlighting
            if actor.being_dragged:
                outline_color, outline_width = "yellow", 4
            elif actor.in_examination:
                outline_color, outline_width = "orange", 3
            elif actor == self.selected_actor:
                outline_color, outline_width = "purple", 3
            else:
                outline_color, outline_width = "black", 2
            
            # Draw actor circle
            self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, 
                                  outline=outline_color, tags="actor", width=outline_width)
            
            # Actor label
            label_parts = [f"{actor.actor_type.value[0]}{actor.actor_id}"]
            if actor.in_examination:
                label_parts.append("📋")
            if actor == self.selected_actor:
                label_parts.append("👆")
            
            label = "".join(label_parts)
            self.canvas.create_text(x, y-25, text=label, font=("Arial", 10, "bold"), 
                                  tags="actor", fill="black")
            
            # Tag ID
            self.canvas.create_text(x, y+20, text=actor.tag_id, font=("Arial", 7), 
                                  tags="actor", fill="gray")
    
    def update_all_metrics(self):
        """Update all performance metrics displays"""
        # Calculate current values
        current_power, sleep_savings = self.simulation.calculate_energy_consumption()
        summary = self.metrics_tracker.get_performance_summary()
        
        # Update metrics
        self.performance_metrics['Total Tasks'].config(
            text=f"Total Tasks: {summary['total_tasks']}"
        )
        self.performance_metrics['Examinations Done'].config(
            text=f"Examinations Done: {summary['examinations']}"
        )
        self.performance_metrics['Prediction Accuracy'].config(
            text=f"Prediction Accuracy: {summary['prediction_accuracy']:.1f}%"
        )
        self.performance_metrics['Time Saved (s)'].config(
            text=f"Time Saved (s): {summary['time_saved_total']:.1f}"
        )
        self.performance_metrics['Time Lost (s)'].config(
            text=f"Time Lost (s): {summary['time_lost_total']:.1f}"
        )
        self.performance_metrics['Net Time Benefit (s)'].config(
            text=f"Net Time Benefit (s): {summary['net_time_benefit']:+.1f}"
        )
        self.performance_metrics['Current Power (kW)'].config(
            text=f"Current Power (kW): {current_power/1000:.2f}"
        )
        self.performance_metrics['Total Power (kW)'].config(
            text=f"Total Power (kW): {summary['energy_consumed_kwh']:.2f}"
        )
        self.performance_metrics['Energy Saved (kWh)'].config(
            text=f"Energy Saved (kWh): {summary['energy_saved_kwh']:.3f}"
        )
    
    def update_equipment_display(self):
        """Update the equipment status display"""
        self.equipment_text.delete(1.0, tk.END)
        
        # Header
        mode = "🔮 PREDICTIVE" if self.simulation.predictive_mode else "⏰ TRADITIONAL"
        self.equipment_text.insert(tk.END, f"Equipment Status - {mode} MODE\n")
        self.equipment_text.insert(tk.END, "=" * 45 + "\n\n")
        
        for room_type, room in self.simulation.rooms.items():
            if room.equipment:
                # Room header with occupancy
                staff_icon = "👩‍⚕️" if room.staff_present else "🚫"
                exam_icon = "📋" if room.examination_in_progress else ""
                doctor_count = len(room.doctors_present)
                patient_count = len(room.patients_present)
                
                self.equipment_text.insert(tk.END, 
                    f"\n{room_type.value} {staff_icon} 👨‍⚕️×{doctor_count} 🤒×{patient_count} {exam_icon}\n")
                self.equipment_text.insert(tk.END, "-" * 30 + "\n")
                
                # Equipment details
                for equipment in room.equipment:
                    power = equipment.get_current_power_consumption()
                    
                    # Status with timing information
                    if equipment.state == EquipmentState.OFF:
                        status = "OFF"
                    elif equipment.state == EquipmentState.STARTING:
                        remaining = max(0, equipment.startup_time - (time.time() - equipment.state_change_time))
                        status = f"STARTING ({remaining:.1f}s)"
                    elif equipment.state == EquipmentState.PRELOADED:
                        status = "PRELOADED"
                    elif equipment.state == EquipmentState.READY:
                        status = "READY"
                    elif equipment.state == EquipmentState.IN_USE:
                        status = f"IN USE"
                    elif equipment.state == EquipmentState.SLEEP:
                        status = "SLEEP (10% power)"
                    elif equipment.state == EquipmentState.SHUTTING_DOWN:
                        remaining = max(0, equipment.shutdown_time - (time.time() - equipment.state_change_time))
                        status = f"SHUTTING DOWN ({remaining:.1f}s)"
                    
                    power_info = f" | {power:.0f}W" if power > 0 else " | 0W"
                    self.equipment_text.insert(tk.END, f"  {equipment.name}: {status}{power_info}\n")
        
        # Auto-scroll to bottom
        self.equipment_text.see(tk.END)
    
    def log_activity(self, message: str):
        """Log activity using the activity logger"""
        formatted_message = self.activity_logger.log_activity(
            message, 
            self.simulation.predictive_mode, 
            self.simulation.auto_simulation_running
        )
        
        # Update the GUI display
        self.activity_text.insert(tk.END, formatted_message + "\n")
        self.activity_text.see(tk.END)
        
        # Keep display manageable (last 200 lines)
        lines = int(self.activity_text.index('end-1c').split('.')[0])
        if lines > 200:
            self.activity_text.delete(1.0, "20.0")
    
    def run(self):
        """Start the application"""
        # Initial welcome messages
        self.log_activity("=== SMART HOSPITAL PREDICTIVE SYSTEM ===")
        self.log_activity("Time & Energy Optimization Demo")
        self.log_activity("Predictive Mode: Equipment preloading")
        self.log_activity("Traditional Mode: Manual activation")
        self.log_activity("Drag actors between rooms")
        self.log_activity("Use Auto Demo for realistic scenarios")
        self.log_activity("Watch time and energy savings!")
        
        try:
            self.root.mainloop()
        finally:
            self.running = False

if __name__ == "__main__":
    print("Starting Smart Hospital Predictive System...")
    print("Time & Energy Optimization Demo")
    
    app = HospitalGUI()
    app.run()
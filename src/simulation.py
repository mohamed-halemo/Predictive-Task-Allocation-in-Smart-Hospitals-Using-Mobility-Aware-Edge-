import random
import time
from typing import List, Dict, Tuple, Optional
from models import RoomType, ActorType, EquipmentState, Position

class Equipment:
    def __init__(self, name: str, startup_time: float, power_consumption: float = 0):
        self.name = name
        self.startup_time = startup_time
        self.shutdown_time = startup_time * 0.3
        self.power_consumption = power_consumption
        self.sleep_power = power_consumption * 0.1
        self.state = EquipmentState.OFF
        self.state_change_time = 0
        self.last_used = 0
        self.idle_start_time = 0
        self.sleep_threshold = 10.0
        self.in_use_by = None
        self.preloaded_by_prediction = False
    
    def start_preload(self):
        """Start preloading equipment (predictive mode)"""
        if self.state in [EquipmentState.OFF, EquipmentState.SLEEP]:
            self.state = EquipmentState.STARTING
            self.state_change_time = time.time()
            self.preloaded_by_prediction = True
            return self.startup_time
        return 0
    
    def start_manual_activation(self):
        """Start manual activation (non-predictive mode)"""
        if self.state in [EquipmentState.OFF, EquipmentState.SLEEP]:
            self.state = EquipmentState.STARTING
            self.state_change_time = time.time()
            self.preloaded_by_prediction = False
            return self.startup_time
        return 0
    
    def update_state(self):
        """Update equipment state based on elapsed time"""
        current_time = time.time()
        elapsed = current_time - self.state_change_time
        
        if self.state == EquipmentState.STARTING:
            if elapsed >= self.startup_time:
                if self.preloaded_by_prediction:
                    self.state = EquipmentState.PRELOADED
                else:
                    self.state = EquipmentState.READY
                    self.idle_start_time = current_time
                return True
        elif self.state == EquipmentState.SHUTTING_DOWN:
            if elapsed >= self.shutdown_time:
                self.state = EquipmentState.OFF
                self.in_use_by = None
                self.preloaded_by_prediction = False
                return True
        elif self.state == EquipmentState.READY:
            if current_time - self.idle_start_time > self.sleep_threshold:
                self.state = EquipmentState.SLEEP
                return True
        
        return False
    
    def get_progress(self):
        """Get startup/shutdown progress (0-1)"""
        if self.state == EquipmentState.STARTING:
            elapsed = time.time() - self.state_change_time
            return min(1.0, elapsed / self.startup_time)
        elif self.state == EquipmentState.SHUTTING_DOWN:
            elapsed = time.time() - self.state_change_time
            return min(1.0, elapsed / self.shutdown_time)
        return 0
    
    def get_current_power_consumption(self):
        """Get current power consumption based on state"""
        if self.state in [EquipmentState.READY, EquipmentState.IN_USE, EquipmentState.PRELOADED]:
            return self.power_consumption
        elif self.state == EquipmentState.SLEEP:
            return self.sleep_power
        elif self.state == EquipmentState.STARTING:
            progress = self.get_progress()
            return self.sleep_power + (self.power_consumption - self.sleep_power) * progress
        else:
            return 0
    
    def activate_preloaded(self):
        """Activate preloaded equipment"""
        if self.state == EquipmentState.PRELOADED:
            self.state = EquipmentState.READY
            self.idle_start_time = time.time()
            return True
        return False
    
    def wake_from_sleep(self):
        """Wake equipment from sleep mode"""
        if self.state == EquipmentState.SLEEP:
            self.state = EquipmentState.READY
            self.idle_start_time = time.time()
            return True
        return False
    
    def start_use(self, user_id):
        """Start using equipment"""
        if ((self.state == EquipmentState.READY) or (self.state == EquipmentState.SLEEP) or (self.state == EquipmentState.PRELOADED)):
            self.state = EquipmentState.IN_USE
            self.in_use_by = user_id
            self.last_used = time.time()
            return True
        
        return False
    
    def stop_use(self):
        """Stop using equipment"""
        if self.state == EquipmentState.IN_USE:
            self.state = EquipmentState.READY
            self.in_use_by = None
            self.idle_start_time = time.time()
            return True
        return False
    
    def start_shutdown(self):
        """Start shutting down equipment"""
        if self.state in [EquipmentState.READY, EquipmentState.IN_USE, EquipmentState.PRELOADED, EquipmentState.SLEEP]:
            self.state = EquipmentState.SHUTTING_DOWN
            self.state_change_time = time.time()
            self.in_use_by = None
            return self.shutdown_time
        return 0

class Room:
    def __init__(self, room_type: RoomType, position: Tuple[int, int], size: Tuple[int, int]):
        self.room_type = room_type
        self.position = position
        self.size = size
        self.equipment = self._initialize_equipment()
        self.occupants = []
        self.staff_present = False
        self.doctors_present = []
        self.patients_present = []
        self.examination_in_progress = False
        self.last_preload_time = 0
        self.equipment_activation_time = 0
        self.last_occupancy_time = time.time()
    
    def _initialize_equipment(self):
        """Initialize realistic medical equipment with accurate specifications"""
        equipment_map = {
            RoomType.ICU: [
                Equipment("Ventilator", 4.0, 800.0),
                Equipment("Heart Monitor", 3.0, 200.0),
                Equipment("IV Pump", 2.5, 150.0),
                Equipment("Defibrillator", 3.5, 400.0)
            ],
            RoomType.RADIOLOGY: [
                Equipment("X-Ray Machine", 5.0, 1500.0),
                Equipment("CT Scanner", 8.0, 3000.0),
                Equipment("MRI", 12.0, 5000.0),
                Equipment("Ultrasound", 3.0, 300.0)
            ],
            RoomType.LAB: [
                Equipment("Blood Analyzer", 4.5, 1200.0),
                Equipment("Microscope", 2.0, 100.0),
                Equipment("Centrifuge", 3.0, 600.0),
                Equipment("PCR Machine", 6.0, 900.0)
            ],
            RoomType.LOBBY: [],
            RoomType.PATIENT_ROOM: [],
            RoomType.EMERGENCY_ROOM: [],
        }
        return equipment_map.get(self.room_type, [])
    
    def update_occupancy(self, actors):
        """Update room occupancy based on current actors"""
        self.staff_present = False
        self.doctors_present = []
        self.patients_present = []
        
        for actor in actors:
            if actor.current_room == self.room_type:
                if actor.actor_type == ActorType.STAFF:
                    self.staff_present = True
                elif actor.actor_type == ActorType.DOCTOR:
                    self.doctors_present.append(actor)
                elif actor.actor_type == ActorType.PATIENT:
                    self.patients_present.append(actor)
        
        if self.staff_present or self.doctors_present or self.patients_present:
            self.last_occupancy_time = time.time()
    
    def start_equipment_preload(self):
        """Start preloading equipment (predictive mode)"""
        total_delay = 0
        preloaded_count = 0
        
        for equipment in self.equipment:
            if equipment.state in [EquipmentState.OFF, EquipmentState.SLEEP]:
                delay = equipment.start_preload()
                total_delay += delay
                preloaded_count += 1
        
        if preloaded_count > 0:
            self.last_preload_time = time.time()
            
        return total_delay, preloaded_count
    
    def staff_enters_room(self):
        """Handle staff entering room - activate equipment"""
        total_delay = 0
        activated_count = 0
        
        for equipment in self.equipment:
            if equipment.state in [EquipmentState.OFF, EquipmentState.SLEEP]:
                delay = equipment.start_manual_activation()
                total_delay += delay
                activated_count += 1
            elif equipment.state == EquipmentState.PRELOADED:
                equipment.activate_preloaded()
                activated_count += 1
        
        if activated_count > 0:
            self.equipment_activation_time = time.time()
        
        return total_delay, activated_count
    
    def check_equipment_ready(self):
        """Check if all equipment is ready for use"""
        if not self.equipment:
            return True
            
        all_ready = True
        for equipment in self.equipment:
            equipment.update_state()
            if equipment.state not in [EquipmentState.READY, EquipmentState.IN_USE, EquipmentState.SLEEP, EquipmentState.PRELOADED]:
                all_ready = False
        
        return all_ready
    
    def start_examination(self):
        """Start examination if conditions are met"""
        if (len(self.doctors_present) > 0 and 
            len(self.patients_present) > 0 and 
            self.check_equipment_ready() and
            not self.examination_in_progress):
            
            doctor = self.doctors_present[0]
            patient = self.patients_present[0]
            user_id = f"D{doctor.actor_id}-P{patient.actor_id}"
            
            for equipment in self.equipment:
                if equipment.state in [EquipmentState.READY, EquipmentState.SLEEP, EquipmentState.PRELOADED]:
                    equipment.start_use(user_id)
            
            self.examination_in_progress = True
            doctor.in_examination = True
            patient.in_examination = True
            doctor.examination_room = self.room_type
            patient.examination_room = self.room_type
            
            return True
        return False
    
    def check_examination_end(self):
        """Check if examination should end"""
        if (self.examination_in_progress and 
            (len(self.doctors_present) == 0 or len(self.patients_present) == 0)):
            
            for equipment in self.equipment:
                equipment.stop_use()
            
            self.examination_in_progress = False
            return True
        return False
    
    def shutdown_equipment(self):
        """Shutdown all equipment when room is empty for too long"""
        shutdown_count = 0
        total_shutdown_time = 0
        
        if time.time() - self.last_occupancy_time > 30.0:
            for equipment in self.equipment:
                shutdown_time = equipment.start_shutdown()
                if shutdown_time > 0:
                    shutdown_count += 1
                    total_shutdown_time += shutdown_time
        
        return shutdown_count, total_shutdown_time
    
    def should_shutdown(self):
        """Determine if equipment should be shut down"""
        return (not self.staff_present and 
                not self.examination_in_progress and 
                len(self.doctors_present) == 0 and 
                len(self.patients_present) == 0 and
                time.time() - self.last_occupancy_time > 30.0)
    
    def get_total_power_consumption(self):
        """Get total power consumption for this room"""
        total_power = 0
        for equipment in self.equipment:
            total_power += equipment.get_current_power_consumption()
        return total_power
    
    def contains_point(self, x: int, y: int) -> bool:
        px, py = self.position
        w, h = self.size
        return px <= x < px + w and py <= y < py + h

class Actor:
    def __init__(self, actor_type: ActorType, actor_id: int, initial_room: RoomType):
        self.actor_type = actor_type
        self.actor_id = actor_id
        self.current_room = initial_room
        self.position = Position(0, 0, initial_room)
        self.movement_history = []
        self.target_room = None
        self.movement_pattern = self._generate_movement_pattern()
        self.canvas_id = None
        self.label_id = None
        self.being_dragged = False
        self.last_movement_time = time.time()
        self.in_examination = False
        self.examination_room = None
        self.auto_movement_target = None
        self.auto_movement_timer = 0
        
        # Basic properties
        self.tag_id = f"{actor_type.value[:1]}{actor_id:03d}"
    
    def _generate_movement_pattern(self):
        if self.actor_type == ActorType.DOCTOR:
            return [RoomType.LOBBY, RoomType.ICU, RoomType.RADIOLOGY, RoomType.LAB, RoomType.LOBBY]
        elif self.actor_type == ActorType.STAFF:
            return [RoomType.LOBBY, RoomType.ICU, RoomType.RADIOLOGY, RoomType.LAB, RoomType.LOBBY]
        else:
            return [RoomType.LOBBY, RoomType.RADIOLOGY, RoomType.LAB, RoomType.ICU, RoomType.LOBBY]
    
    def get_next_likely_room(self) -> RoomType:
        if not self.movement_history:
            pattern_start = 1 if len(self.movement_pattern) > 1 else 0
            return self.movement_pattern[pattern_start]
        
        try:
            current_index = self.movement_pattern.index(self.current_room)
            next_index = (current_index + 1) % len(self.movement_pattern)
            return self.movement_pattern[next_index]
        except ValueError:
            return random.choice([r for r in list(RoomType) if r != self.current_room])

class PredictionEngine:
    def __init__(self):
        self.prediction_accuracy = 0.0
        self.total_predictions = 0
        self.correct_predictions = 0
        self.staff_movement_patterns = {}
        self.recent_predictions = []
    
    def learn_staff_pattern(self, staff_actor, rooms):
        """Learn from staff movement patterns"""
        if staff_actor.actor_type == ActorType.STAFF:
            if staff_actor.actor_id not in self.staff_movement_patterns:
                self.staff_movement_patterns[staff_actor.actor_id] = []
            
            self.staff_movement_patterns[staff_actor.actor_id].append({
                'room': staff_actor.current_room,
                'timestamp': time.time()
            })
            
            # Keep only recent movements (last 20)
            if len(self.staff_movement_patterns[staff_actor.actor_id]) > 20:
                self.staff_movement_patterns[staff_actor.actor_id].pop(0)
    
    def predict_movement(self, actor, rooms):
        predicted_room = actor.get_next_likely_room()
        confidence = 0.7  # Base confidence
        
        self.total_predictions += 1
        
        prediction_data = {
            'actor_id': actor.actor_id,
            'predicted_room': predicted_room,
            'current_room': actor.current_room,
            'confidence': confidence,
            'timestamp': time.time()
        }
        self.recent_predictions.append(prediction_data)
        
        if len(self.recent_predictions) > 50:
            self.recent_predictions.pop(0)
        
        return predicted_room, confidence
    
    def update_accuracy(self, predicted: RoomType, actual: RoomType):
        if predicted == actual:
            self.correct_predictions += 1
        if self.total_predictions > 0:
            self.prediction_accuracy = (self.correct_predictions / self.total_predictions) * 100

class HospitalSimulation:
    def __init__(self):
        self.rooms = self._create_rooms()
        self.actors = []
        self.prediction_engine = PredictionEngine()
        self.running = False
        self.auto_simulation_running = False
        self.predictive_mode = True
        
        # Metrics will be handled by the metrics module
        self.metrics = {
            'total_delay_saved': 0,
            'total_delay_incurred': 0,
            'tasks_completed': 0,
            'resources_preloaded': 0,
            'manual_movements': 0,
            'equipment_activations': 0,
            'examinations_completed': 0,
            'equipment_shutdowns': 0,
            'time_savings_per_movement': [],
            'total_time_saved': 0,
            'total_energy_consumed': 0,
            'energy_saved_sleep': 0
        }
        
        self.movement_log = []
        self.auto_simulation_step = 0
        self.start_time = time.time()
        self.last_energy_update = time.time()
    
    def _create_rooms(self):
        return {
            RoomType.RADIOLOGY: Room(RoomType.RADIOLOGY, (0, 0), (300, 200)),
            RoomType.ICU: Room(RoomType.ICU, (0, 200), (300, 200)),
            RoomType.LOBBY: Room(RoomType.LOBBY, (300, 0), (300, 200)),
            RoomType.LAB: Room(RoomType.LAB, (300, 200), (300, 200)),
            RoomType.PATIENT_ROOM: Room(RoomType.PATIENT_ROOM, (600, 0), (300, 200)),
            RoomType.EMERGENCY_ROOM: Room(RoomType.EMERGENCY_ROOM, (600, 200), (300, 200))
        }
    
    def set_predictive_mode(self, mode: bool):
        """Switch between predictive and non-predictive mode"""
        self.predictive_mode = mode
        if not mode:
            for room in self.rooms.values():
                for equipment in room.equipment:
                    if equipment.state == EquipmentState.PRELOADED:
                        equipment.state = EquipmentState.OFF
    
    def add_actor(self, actor_type: ActorType):
        actor_id = len([a for a in self.actors if a.actor_type == actor_type])
        initial_room = RoomType.LOBBY
        actor = Actor(actor_type, actor_id, initial_room)
        
        room = self.rooms[initial_room]
        actor.position.x = room.position[0] + 50 + (actor_id * 40)
        actor.position.y = room.position[1] + 100 + (actor_id * 20)
        
        actor.position.x = min(actor.position.x, room.position[0] + room.size[0] - 50)
        actor.position.y = min(actor.position.y, room.position[1] + room.size[1] - 50)
        
        self.actors.append(actor)
        return actor
    
    def remove_actor(self, actor):
        """Remove an actor from the simulation"""
        if actor in self.actors:
            if actor.in_examination:
                actor.in_examination = False
                actor.examination_room = None
            self.actors.remove(actor)
    
    def update_all_rooms(self):
        """Update all room states and handle equipment transitions"""
        for room in self.rooms.values():
            room.update_occupancy(self.actors)
            room.check_equipment_ready()
            
            if room.start_examination():
                self.metrics['examinations_completed'] += 1
            
            if room.check_examination_end():
                for actor in self.actors:
                    if actor.examination_room == room.room_type:
                        actor.in_examination = False
                        actor.examination_room = None
            
            if room.should_shutdown() and self.predictive_mode:
                shutdown_count, shutdown_time = room.shutdown_equipment()
                if shutdown_count > 0:
                    self.metrics['equipment_shutdowns'] += shutdown_count
    
    def calculate_energy_consumption(self):
        """Calculate current energy consumption and sleep savings"""
        current_time = time.time()
        dt = current_time - self.last_energy_update
        self.last_energy_update = current_time
        
        total_power = 0
        sleep_savings = 0
        
        for room in self.rooms.values():
            room_power = room.get_total_power_consumption()
            total_power += room_power
            
            for equipment in room.equipment:
                if equipment.state == EquipmentState.SLEEP:
                    power_saved = equipment.power_consumption - equipment.sleep_power
                    sleep_savings += power_saved * dt / 3600
        
        energy_consumed = total_power * dt / 3600
        self.metrics['total_energy_consumed'] += energy_consumed
        self.metrics['energy_saved_sleep'] += sleep_savings
        
        return total_power, sleep_savings
    
    def move_actor_to_position(self, actor: Actor, canvas_x: int, canvas_y: int):
        """Move actor to specific canvas position and handle workflow"""
        new_room = self._get_room_from_position(canvas_x, canvas_y)
        old_room = actor.current_room
        # Update actor position
        actor.position.x = canvas_x
        actor.position.y = canvas_y
        actor.position.room = new_room
        if new_room != old_room:
            actor.current_room = new_room
            actor.movement_history.append(old_room)
            actor.last_movement_time = time.time()
            # Only activate devices if nurse enters (manual activation)
            if actor.actor_type == ActorType.STAFF and new_room != RoomType.LOBBY:
                room = self.rooms[new_room]
                room.staff_enters_room()

    def auto_simulation_step_execute(self):
        """Perform one step of automated simulation"""
        if not self.actors:
            return False
        
        simulation_sequences = [
            # Start from Lobby to Emergency Room
            {'actor_type': ActorType.STAFF, 'target_room': RoomType.EMERGENCY_ROOM, 'delay': 2},
            {'actor_type': ActorType.DOCTOR, 'target_room': RoomType.EMERGENCY_ROOM, 'delay': 3},
            {'actor_type': ActorType.PATIENT, 'target_room': RoomType.EMERGENCY_ROOM, 'delay': 5},

            # Radiology
            {'actor_type': ActorType.STAFF, 'target_room': RoomType.RADIOLOGY, 'delay': 2},
            {'actor_type': ActorType.DOCTOR, 'target_room': RoomType.RADIOLOGY, 'delay': 3},
            {'actor_type': ActorType.PATIENT, 'target_room': RoomType.RADIOLOGY, 'delay': 5},

            # Laboratory
            {'actor_type': ActorType.STAFF, 'target_room': RoomType.LAB, 'delay': 2},
            {'actor_type': ActorType.DOCTOR, 'target_room': RoomType.LAB, 'delay': 3},
            {'actor_type': ActorType.PATIENT, 'target_room': RoomType.LAB, 'delay': 4},

            # ICU
            {'actor_type': ActorType.STAFF, 'target_room': RoomType.ICU, 'delay': 2},
            {'actor_type': ActorType.DOCTOR, 'target_room': RoomType.ICU, 'delay': 3},
            {'actor_type': ActorType.PATIENT, 'target_room': RoomType.ICU, 'delay': 5},
        ]
        
        if self.auto_simulation_step < len(simulation_sequences):
            step = simulation_sequences[self.auto_simulation_step]
            
            actors_of_type = [a for a in self.actors if a.actor_type == step['actor_type']]
            if actors_of_type:
                actor = actors_of_type[0]
                target_room = step['target_room']
                
                room = self.rooms[target_room]
                target_x = room.position[0] + room.size[0] // 2
                target_y = room.position[1] + room.size[1] // 2
                
                self.move_actor_to_position(actor, target_x, target_y)
                
            self.auto_simulation_step += 1
            return True
        else:
            self.auto_simulation_step = 0
            return False
    
    def auto_simulation_step_execute_predictive(self):
        """Perform one step of automated simulation with predictive preloading."""
        if not self.actors:
            return False
        # Define the sequence
        sequence = [
            RoomType.LOBBY,
            RoomType.EMERGENCY_ROOM,
            RoomType.RADIOLOGY,
            RoomType.LAB,
            RoomType.ICU
        ]
        if not hasattr(self, 'predictive_step'):
            self.predictive_step = 0
            self.predictive_stage = 0
        if self.predictive_step >= len(sequence):
            self.predictive_step = 0
            self.predictive_stage = 0
            return False
        room = self.rooms[sequence[self.predictive_step]]
        x = room.position[0] + room.size[0] // 2
        y = room.position[1] + room.size[1] // 2
        nurse = self.get_actor(ActorType.STAFF)
        doctor = self.get_actor(ActorType.DOCTOR)
        patient = self.get_actor(ActorType.PATIENT)
        # Movement logic
        if self.predictive_stage == 0:
            if nurse.current_room != sequence[self.predictive_step]:
                self.move_actor_to_position(nurse, x, y)
                return True
            # Nurse has just arrived in the new room, now trigger preloading for the next rooms
            if sequence[self.predictive_step] == RoomType.EMERGENCY_ROOM:
                self.rooms[RoomType.RADIOLOGY].start_equipment_preload()
                self.rooms[RoomType.LAB].start_equipment_preload()
            if sequence[self.predictive_step] == RoomType.LAB:
                self.rooms[RoomType.ICU].start_equipment_preload()
            self.predictive_stage = 1
            return True
        elif self.predictive_stage == 1:
            if doctor.current_room != sequence[self.predictive_step]:
                self.move_actor_to_position(doctor, x, y)
                return True
            self.predictive_stage = 2
            return True
        elif self.predictive_stage == 2:
            if patient.current_room != sequence[self.predictive_step]:
                self.move_actor_to_position(patient, x, y)
                return True
            self.predictive_step += 1
            self.predictive_stage = 0
            return True
        return False
    
    def reset_predictive_auto_demo(self):
        self.predictive_step = 0
        self.predictive_stage = 0

    def _get_room_from_position(self, x: int, y: int) -> RoomType:
        for room_type, room in self.rooms.items():
            if room.contains_point(x, y):
                return room_type
        return RoomType.LOBBY
    
    def get_performance_summary(self):
        """Get comprehensive performance summary"""
        runtime = time.time() - self.start_time
        avg_time_per_task = self.metrics['total_time_saved'] / max(1, self.metrics['tasks_completed'])
        energy_efficiency = self.metrics['energy_saved_sleep'] / max(1, self.metrics['total_energy_consumed']) * 100
        
        return {
            'runtime_minutes': runtime / 60,
            'total_tasks': self.metrics['tasks_completed'],
            'examinations': self.metrics['examinations_completed'],
            'prediction_accuracy': self.prediction_engine.prediction_accuracy,
            'time_saved_total': self.metrics['total_delay_saved'],
            'time_lost_total': self.metrics['total_delay_incurred'],
            'net_time_benefit': self.metrics['total_time_saved'],
            'avg_time_per_task': avg_time_per_task,
            'energy_consumed_kwh': self.metrics['total_energy_consumed'] / 1000,
            'energy_saved_kwh': self.metrics['energy_saved_sleep'] / 1000,
            'energy_efficiency_percent': energy_efficiency,
            'resources_preloaded': self.metrics['resources_preloaded']
        }

    def get_actor(self, actor_type):
        """Return the first actor of the given type, or None if not found."""
        return next((a for a in self.actors if a.actor_type == actor_type), None)
import time
from typing import List, Dict, Any, Optional
from models import ActorType, RoomType

class ActivityLogger:
    """Handles all activity logging for the hospital simulation"""
    
    def __init__(self):
        self.activity_log = []
        self.max_log_size = 200
    
    def log_activity(self, message: str, predictive_mode: bool = True, auto_mode: bool = False):
        """Log activity with timestamp and mode information"""
        timestamp = time.strftime("%H:%M:%S")
        mode = "PRED" if predictive_mode else "TRAD"
        auto = "AUTO" if auto_mode else "MAN"
        
        formatted_message = f"[{timestamp}] [{mode}] [{auto}] {message}"
        self.activity_log.append(formatted_message)
        
        # Keep log manageable
        if len(self.activity_log) > self.max_log_size:
            self.activity_log.pop(0)
        
        return formatted_message
    
    def get_recent_activities(self, count: int = 20) -> List[str]:
        """Get the most recent activities"""
        return self.activity_log[-count:] if self.activity_log else []
    
    def clear_log(self):
        """Clear the activity log"""
        self.activity_log.clear()
    
    def export_log(self, filename: str = None) -> str:
        """Export log to file or return as string"""
        log_content = "\n".join(self.activity_log)
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(log_content)
                return f"Log exported to {filename}"
            except Exception as e:
                return f"Error exporting log: {e}"
        
        return log_content

class MetricsTracker:
    """Handles metrics tracking and analysis for the hospital simulation"""
    
    def __init__(self):
        self.reset_metrics()
    
    def reset_metrics(self):
        """Reset all metrics to initial state"""
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
        self.start_time = time.time()
        self.last_energy_update = time.time()
    
    def log_movement(self, movement_info: Dict[str, Any]):
        """Log a movement event with detailed information"""
        self.movement_log.append(movement_info)
        
        # Update metrics
        self.metrics['tasks_completed'] += 1
        self.metrics['manual_movements'] += 1
        self.metrics['total_delay_saved'] += movement_info.get('time_saved', 0)
        self.metrics['total_delay_incurred'] += movement_info.get('delay_incurred', 0)
        self.metrics['total_time_saved'] += movement_info.get('net_effect', 0)
        self.metrics['time_savings_per_movement'].append(movement_info.get('net_effect', 0))
    
    def update_energy_metrics(self, energy_consumed: float, sleep_savings: float):
        """Update energy consumption metrics"""
        self.metrics['total_energy_consumed'] += energy_consumed
        self.metrics['energy_saved_sleep'] += sleep_savings
    
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def get_performance_summary(self, prediction_accuracy: float = 0.0) -> Dict[str, Any]:
        """Generate comprehensive performance summary"""
        runtime = time.time() - self.start_time
        avg_time_per_task = self.metrics['total_time_saved'] / max(1, self.metrics['tasks_completed'])
        energy_efficiency = self.metrics['energy_saved_sleep'] / max(1, self.metrics['total_energy_consumed']) * 100
        
        return {
            'runtime_minutes': runtime / 60,
            'total_tasks': self.metrics['tasks_completed'],
            'examinations': self.metrics['examinations_completed'],
            'prediction_accuracy': prediction_accuracy,
            'time_saved_total': self.metrics['total_delay_saved'],
            'time_lost_total': self.metrics['total_delay_incurred'],
            'net_time_benefit': self.metrics['total_time_saved'],
            'avg_time_per_task': avg_time_per_task,
            'energy_consumed_kwh': self.metrics['total_energy_consumed'] / 1000,
            'energy_saved_kwh': self.metrics['energy_saved_sleep'] / 1000,
            'energy_efficiency_percent': energy_efficiency,
            'resources_preloaded': self.metrics['resources_preloaded']
        }
    
    def get_movement_analysis(self) -> Dict[str, Any]:
        """Analyze movement patterns and efficiency"""
        if not self.movement_log:
            return {'message': 'No movements recorded yet'}
        
        # Calculate movement statistics
        time_effects = [m['net_effect'] for m in self.movement_log]
        positive_effects = [t for t in time_effects if t > 0]
        negative_effects = [t for t in time_effects if t < 0]
        
        # Room transition analysis
        room_transitions = {}
        for movement in self.movement_log:
            transition = f"{movement['from_room']} → {movement['to_room']}"
            if transition not in room_transitions:
                room_transitions[transition] = {'count': 0, 'avg_effect': 0, 'total_effect': 0}
            room_transitions[transition]['count'] += 1
            room_transitions[transition]['total_effect'] += movement['net_effect']
            room_transitions[transition]['avg_effect'] = (
                room_transitions[transition]['total_effect'] / room_transitions[transition]['count']
            )
        
        # Actor type analysis
        actor_performance = {}
        for movement in self.movement_log:
            actor_type = movement['actor_type']
            if actor_type not in actor_performance:
                actor_performance[actor_type] = {'movements': 0, 'total_effect': 0, 'avg_effect': 0}
            actor_performance[actor_type]['movements'] += 1
            actor_performance[actor_type]['total_effect'] += movement['net_effect']
            actor_performance[actor_type]['avg_effect'] = (
                actor_performance[actor_type]['total_effect'] / actor_performance[actor_type]['movements']
            )
        
        return {
            'total_movements': len(self.movement_log),
            'positive_outcomes': len(positive_effects),
            'negative_outcomes': len(negative_effects),
            'neutral_outcomes': len(time_effects) - len(positive_effects) - len(negative_effects),
            'avg_time_effect': sum(time_effects) / len(time_effects),
            'best_effect': max(time_effects) if time_effects else 0,
            'worst_effect': min(time_effects) if time_effects else 0,
            'room_transitions': room_transitions,
            'actor_performance': actor_performance
        }
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to file or return as formatted string"""
        summary = self.get_performance_summary()
        analysis = self.get_movement_analysis()
        
        report = f"""
HOSPITAL SIMULATION METRICS REPORT
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
========================================

PERFORMANCE SUMMARY:
- Runtime: {summary['runtime_minutes']:.2f} minutes
- Total Tasks: {summary['total_tasks']}
- Examinations: {summary['examinations']}
- Prediction Accuracy: {summary['prediction_accuracy']:.1f}%
- Time Saved: {summary['time_saved_total']:.2f}s
- Time Lost: {summary['time_lost_total']:.2f}s
- Net Benefit: {summary['net_time_benefit']:.2f}s
- Energy Consumed: {summary['energy_consumed_kwh']:.3f} kWh
- Energy Saved: {summary['energy_saved_kwh']:.3f} kWh

MOVEMENT ANALYSIS:
- Total Movements: {analysis.get('total_movements', 0)}
- Positive Outcomes: {analysis.get('positive_outcomes', 0)}
- Negative Outcomes: {analysis.get('negative_outcomes', 0)}
- Average Time Effect: {analysis.get('avg_time_effect', 0):.2f}s

DETAILED MOVEMENT LOG:
"""
        
        for i, movement in enumerate(self.movement_log, 1):
            report += f"{i:3d}. {movement['actor_type']} {movement['actor_id']}: "
            report += f"{movement['from_room']} → {movement['to_room']} "
            report += f"(Effect: {movement['net_effect']:+.1f}s)\n"
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(report)
                return f"Metrics exported to {filename}"
            except Exception as e:
                return f"Error exporting metrics: {e}"
        
        return report

class PerformanceAnalyzer:
    """Advanced performance analysis for the hospital simulation"""
    
    def __init__(self, metrics_tracker: MetricsTracker):
        self.metrics_tracker = metrics_tracker
    
    def analyze_prediction_effectiveness(self, prediction_engine) -> Dict[str, Any]:
        """Analyze the effectiveness of the prediction engine"""
        if not prediction_engine.recent_predictions:
            return {'message': 'No predictions made yet'}
        
        correct_predictions = 0
        total_predictions = len(prediction_engine.recent_predictions)
        
        confidence_levels = [p['confidence'] for p in prediction_engine.recent_predictions]
        avg_confidence = sum(confidence_levels) / len(confidence_levels)
        
        # Analyze prediction accuracy by confidence level
        high_confidence_predictions = [p for p in prediction_engine.recent_predictions if p['confidence'] > 0.8]
        high_confidence_accuracy = 0
        if high_confidence_predictions:
            # This would need actual movement outcomes to calculate properly
            # For now, we'll use the overall accuracy
            high_confidence_accuracy = prediction_engine.prediction_accuracy
        
        return {
            'total_predictions': total_predictions,
            'accuracy_percent': prediction_engine.prediction_accuracy,
            'average_confidence': avg_confidence,
            'high_confidence_accuracy': high_confidence_accuracy,
            'predictions_per_minute': total_predictions / max(1, (time.time() - self.metrics_tracker.start_time) / 60)
        }
    
    def analyze_energy_efficiency(self, simulation) -> Dict[str, Any]:
        """Analyze energy efficiency patterns"""
        total_power = 0
        sleep_power = 0
        active_equipment = 0
        sleeping_equipment = 0
        
        for room in simulation.rooms.values():
            for equipment in room.equipment:
                if equipment.state.value in ['READY', 'IN_USE', 'PRELOADED']:
                    total_power += equipment.power_consumption
                    active_equipment += 1
                elif equipment.state.value == 'SLEEP':
                    sleep_power += equipment.sleep_power
                    sleeping_equipment += 1
        
        efficiency_ratio = sleep_power / max(1, total_power) * 100
        
        return {
            'current_total_power_kw': total_power / 1000,
            'current_sleep_power_kw': sleep_power / 1000,
            'active_equipment_count': active_equipment,
            'sleeping_equipment_count': sleeping_equipment,
            'sleep_efficiency_percent': efficiency_ratio,
            'total_energy_saved_kwh': self.metrics_tracker.metrics['energy_saved_sleep'] / 1000
        }
    
    def generate_recommendations(self, simulation) -> List[str]:
        """Generate optimization recommendations based on current performance"""
        recommendations = []
        summary = self.metrics_tracker.get_performance_summary(simulation.prediction_engine.prediction_accuracy)
        
        # Time efficiency recommendations
        if summary['net_time_benefit'] < 0:
            recommendations.append("Consider optimizing prediction algorithm - current net time benefit is negative")
        elif summary['net_time_benefit'] < 10:
            recommendations.append(" Prediction system shows marginal benefits - consider tuning confidence thresholds")
        
        # Prediction accuracy recommendations
        if summary['prediction_accuracy'] < 70:
            recommendations.append(" Prediction accuracy is below 70% - review movement pattern learning")
        elif summary['prediction_accuracy'] > 90:
            recommendations.append(" Excellent prediction accuracy! Consider expanding to more complex scenarios")
        
        # Energy efficiency recommendations
        if summary['energy_efficiency_percent'] < 5:
            recommendations.append(" Low energy savings from sleep mode - check sleep threshold settings")
        elif summary['energy_efficiency_percent'] > 20:
            recommendations.append(" Great energy efficiency! Sleep mode is working well")
        
        # Activity level recommendations
        if summary['total_tasks'] < 10:
            recommendations.append(" Low activity level - consider running auto simulation for better metrics")
        
        if not recommendations:
            recommendations.append(" System is performing well across all metrics!")
        
        return recommendations
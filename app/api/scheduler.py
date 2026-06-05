"""
Task scheduler for background jobs

Phase 2.3: Scheduled Tasks

Author: TANGO
Last Updated: June 5, 2026
"""

import logging
import asyncio
from datetime import datetime, time
from typing import Optional, Callable, Dict, List

logger = logging.getLogger(__name__)


class SimpleScheduler:
    """Simple task scheduler without external dependencies."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.is_running = False
        self._loop_task: Optional[asyncio.Task] = None
    
    def add_job(self, job_id: str, func: Callable, interval_minutes: int = 60,
                description: str = "") -> None:
        """Add a scheduled job."""
        self.tasks[job_id] = {
            'func': func,
            'interval_minutes': interval_minutes,
            'description': description,
            'last_run': None,
            'next_run': datetime.utcnow(),
            'run_count': 0,
            'failures': 0,
            'enabled': True
        }
        logger.info(f"Job added: {job_id} - {description} (interval: {interval_minutes}m)")
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        if job_id in self.tasks:
            del self.tasks[job_id]
            logger.info(f"Job removed: {job_id}")
            return True
        return False
    
    def enable_job(self, job_id: str) -> bool:
        """Enable a job."""
        if job_id in self.tasks:
            self.tasks[job_id]['enabled'] = True
            logger.info(f"Job enabled: {job_id}")
            return True
        return False
    
    def disable_job(self, job_id: str) -> bool:
        """Disable a job."""
        if job_id in self.tasks:
            self.tasks[job_id]['enabled'] = False
            logger.info(f"Job disabled: {job_id}")
            return True
        return False
    
    async def _run_job(self, job_id: str) -> None:
        """Run a single job."""
        job = self.tasks[job_id]
        
        try:
            logger.info(f"Running job: {job_id}")
            func = job['func']
            
            # Handle async and sync functions
            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                func()
            
            job['last_run'] = datetime.utcnow()
            job['run_count'] += 1
            job['next_run'] = datetime.utcnow() + \
                __import__('datetime').timedelta(minutes=job['interval_minutes'])
            
            logger.info(f"Job completed: {job_id} (run #{job['run_count']})")
        
        except Exception as e:
            job['failures'] += 1
            logger.error(f"Job failed: {job_id} - {str(e)}")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler started")
        
        while self.is_running:
            try:
                now = datetime.utcnow()
                
                # Check each task
                for job_id, job in self.tasks.items():
                    if not job['enabled']:
                        continue
                    
                    if now >= job['next_run']:
                        await self._run_job(job_id)
                
                # Sleep for a short period before checking again
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        self._loop_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler started successfully")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return
        
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Scheduler stopped")
    
    def get_job_info(self, job_id: str) -> Optional[Dict]:
        """Get information about a job."""
        if job_id not in self.tasks:
            return None
        
        job = self.tasks[job_id]
        return {
            'job_id': job_id,
            'description': job['description'],
            'interval_minutes': job['interval_minutes'],
            'enabled': job['enabled'],
            'last_run': job['last_run'],
            'next_run': job['next_run'],
            'run_count': job['run_count'],
            'failures': job['failures']
        }
    
    def get_all_jobs(self) -> List[Dict]:
        """Get information about all jobs."""
        return [self.get_job_info(job_id) for job_id in self.tasks.keys()]
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            'is_running': self.is_running,
            'total_jobs': len(self.tasks),
            'enabled_jobs': sum(1 for j in self.tasks.values() if j['enabled']),
            'disabled_jobs': sum(1 for j in self.tasks.values() if not j['enabled']),
            'total_runs': sum(j['run_count'] for j in self.tasks.values()),
            'total_failures': sum(j['failures'] for j in self.tasks.values()),
            'jobs': self.get_all_jobs()
        }


# Global scheduler instance
_scheduler: Optional[SimpleScheduler] = None


def get_scheduler() -> SimpleScheduler:
    """Get or create scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SimpleScheduler()
        logger.info("Scheduler initialized")
    return _scheduler


async def init_scheduler(jobs: Dict[str, tuple]) -> None:
    """Initialize scheduler with jobs.
    
    Args:
        jobs: Dict of {job_id: (func, interval_minutes, description)}
    """
    scheduler = get_scheduler()
    
    for job_id, (func, interval, description) in jobs.items():
        scheduler.add_job(job_id, func, interval, description)
    
    await scheduler.start()


async def shutdown_scheduler() -> None:
    """Shutdown scheduler."""
    scheduler = get_scheduler()
    await scheduler.stop()

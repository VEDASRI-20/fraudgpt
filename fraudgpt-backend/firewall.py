import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List
import ipaddress
import logging
from threading import Lock

logger = logging.getLogger(__name__)

class Firewall:
    def __init__(self, config_path: str):
        """Initialize firewall with configuration from JSON file."""
        self.whitelist = []
        self.blacklist = []
        self.rate_limit_requests = 100
        self.rate_limit_window = 60  # seconds
        self.log_file = "firewall_logs.csv"
        self.request_counts: Dict[str, List[datetime]] = {}
        self.lock = Lock()  # Thread-safe access
        self.load_config(config_path)
        self.initialize_log_file()

    def load_config(self, config_path: str):
        """Load firewall configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.whitelist = [ipaddress.ip_network(ip) for ip in config.get('whitelist', [])]
            self.blacklist = [ipaddress.ip_network(ip) for ip in config.get('blacklist', [])]
            self.rate_limit_requests = config.get('rate_limit', {}).get('requests', 100)
            self.rate_limit_window = config.get('rate_limit', {}).get('window_seconds', 60)
            self.log_file = config.get('log_file', 'firewall_logs.csv')
            logger.info(f"Firewall configured: {len(self.whitelist)} whitelisted, {len(self.blacklist)} blacklisted IPs")
        except Exception as e:
            logger.error(f"Error loading firewall config: {e}")
            # Use defaults if config fails

    def initialize_log_file(self):
        """Initialize the firewall log file with headers."""
        try:
            with self.lock, open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(['timestamp', 'ip_address', 'status', 'details'])
        except Exception as e:
            logger.error(f"Error initializing log file {self.log_file}: {e}")

    def is_allowed_ip(self, ip: str) -> bool:
        """Check if an IP is allowed based on whitelist and blacklist."""
        try:
            ip_addr = ipaddress.ip_address(ip)
            # Check whitelist first
            if any(ip_addr in net for net in self.whitelist):
                return True
            # Check blacklist
            if any(ip_addr in net for net in self.blacklist):
                return False
            return True
        except ValueError:
            logger.error(f"Invalid IP address format: {ip}")
            return False

    def check_rate_limit(self, ip: str) -> bool:
        """Check if the IP is within rate limits."""
        with self.lock:
            now = datetime.utcnow()
            if ip not in self.request_counts:
                self.request_counts[ip] = []
            # Remove requests older than the window
            self.request_counts[ip] = [
                t for t in self.request_counts[ip]
                if now - t < timedelta(seconds=self.rate_limit_window)
            ]
            # Add current request
            self.request_counts[ip].append(now)
            return len(self.request_counts[ip]) <= self.rate_limit_requests

    def log_request(self, ip: str, status: str):
        """Log a request to the firewall log file."""
        try:
            with self.lock, open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.utcnow().isoformat(), ip, status, ""])
        except Exception as e:
            logger.error(f"Error logging to {self.log_file}: {e}")

    def get_stats(self) -> Dict:
        """Return firewall statistics."""
        with self.lock:
            return {
                "whitelisted_ips": len(self.whitelist),
                "blacklisted_ips": len(self.blacklist),
                "active_ips": len(self.request_counts),
                "rate_limit_requests": self.rate_limit_requests,
                "rate_limit_window_seconds": self.rate_limit_window
            }
"""
Main entry point for the Enhanced Crowd Monitoring System.
"""

import argparse
import sys

import cv2

from config import MonitoringConfig
from logger_config import get_logger
from monitor import CrowdMonitor

logger = get_logger(__name__)


def parse_arguments() -> MonitoringConfig:
    """
    Parse command line arguments and create configuration.
    
    Returns:
        Monitoring configuration object
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Crowd Monitoring System with Interactive Features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Video source and model
    parser.add_argument("--source", type=str, default="0",
                        help="Video source (camera index or video file path)")
    parser.add_argument("--model", type=str, default="model/yolov8n.pt",
                        help="YOLO model path")

    # Spatial parameters
    parser.add_argument("--cell-width", type=float, default=2.0,
                        help="Grid cell width in meters")
    parser.add_argument("--cell-height", type=float, default=2.0,
                        help="Grid cell height in meters")
    parser.add_argument("--person-radius", type=float, default=2,
                        help="Person radius for capacity calculation (meters)")

    # Detection parameters
    parser.add_argument("--detect-every", type=int, default=3,
                        help="Run detection every N frames")
    parser.add_argument("--conf", type=float, default=0.35,
                        help="Detection confidence threshold")
    parser.add_argument("--min-bbox-area", type=int, default=1500,
                        help="Minimum bounding box area")

    # Tracking parameters
    parser.add_argument("--use-deepsort", action="store_true",
                        help="Use DeepSort tracker (requires installation)")
    parser.add_argument("--max-age", type=int, default=30,
                        help="Maximum age for tracks")
    parser.add_argument("--n-init", type=int, default=1,
                        help="Number of frames to confirm track")

    # Smoothing and alert settings
    parser.add_argument("--ema-alpha", type=float, default=0.4,
                        help="EMA smoothing factor")
    parser.add_argument("--fps", type=float, default=15.0,
                        help="Expected FPS for timing calculations")
    parser.add_argument("--hysteresis", type=float, default=3.0,
                        help="Alert hysteresis time in seconds")

    # Interactive features
    parser.add_argument("--disable-screenshots", action="store_true",
                        help="Disable screenshot functionality")
    parser.add_argument("--disable-grid-adjustment", action="store_true",
                        help="Disable runtime grid adjustment")

    args = parser.parse_args()

    # Create configuration object
    config = MonitoringConfig(
        source=args.source,
        model_path=args.model,
        cell_width=args.cell_width,
        cell_height=args.cell_height,
        person_radius=args.person_radius,
        detect_every=args.detect_every,
        confidence_threshold=args.conf,
        min_bbox_area=args.min_bbox_area,
        use_deepsort=args.use_deepsort,
        max_age=args.max_age,
        n_init=args.n_init,
        ema_alpha=args.ema_alpha,
        fps=args.fps,
        hysteresis_time=args.hysteresis,
        enable_screenshots=not args.disable_screenshots,
        enable_grid_adjustment=not args.disable_grid_adjustment
    )

    return config


def main():
    """Main entry point"""
    try:
        # Parse configuration
        config = parse_arguments()

        logger.info("=== Enhanced Crowd Monitoring System ===")
        logger.info(f"Video source: {config.source}")
        logger.info(f"YOLO model: {config.model_path}")
        logger.info(f"Grid cell size: {config.cell_width}x{config.cell_height}m")
        logger.info(f"Person radius: {config.person_radius}m")
        logger.info(f"Using tracker: {'DeepSort' if config.use_deepsort else 'Centroid'}")
        logger.info(f"Interactive features: Screenshots={config.enable_screenshots}, "
                    f"Grid adjustment={config.enable_grid_adjustment}")

        # Initialize and run monitoring system
        monitor = CrowdMonitor(config)
        success = monitor.initialize()

        if success:
            logger.info("Monitoring completed successfully")
        else:
            logger.error("Monitoring failed to initialize")
            return 1

    except KeyboardInterrupt:
        logger.info("System interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"System error: {e}")
        return 1
    finally:
        # Cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

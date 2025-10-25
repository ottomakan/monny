# Monitoring

This codebase contains project-specific monitoring tools that are custom built over and above the standard monitoring solutions that are available.

## Purpose

The purpose of this repository is to provide specialized monitoring capabilities tailored to specific project requirements. While standard monitoring tools provide general-purpose observability, this codebase focuses on custom-built solutions that address unique monitoring needs that cannot be adequately covered by off-the-shelf solutions.

## Structure

- `supra/` - Contains monitoring tools specific to Supra blockchain infrastructure
  - `block_health.py` - Health monitoring for Supra blockchain operations, including commit tracking, QC monitoring, and height monotonicity checks

## Custom Monitoring Approach

Rather than relying solely on generic monitoring platforms, this codebase implements:

- **Project-specific metrics** that are not available in standard monitoring tools
- **Custom health checks** tailored to specific application behaviors
- **Specialized log parsing** for domain-specific events and patterns
- **Targeted alerting** based on project-specific thresholds and conditions

This approach ensures that critical project-specific behaviors are monitored with the precision and detail required for reliable operations.

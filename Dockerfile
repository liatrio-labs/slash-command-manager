# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN pip install uv

# Copy required files for package building
COPY pyproject.toml uv.lock LICENSE README.md ./

# Install dependencies (without building the package yet)
RUN uv sync --no-install-project

# Copy source code
COPY . .

# Install the package in development mode
RUN uv pip install -e .

# Create a non-root user for security
RUN useradd -m -u 1000 slashuser && chown -R slashuser:slashuser /app
USER slashuser

# Set the default command to show help
ENTRYPOINT ["uv", "run", "slash-man"]
CMD ["--help"]

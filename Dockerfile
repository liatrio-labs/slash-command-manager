# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN pip install uv==0.5.0

# Copy required files for package building
COPY pyproject.toml uv.lock LICENSE README.md ./

# Copy source code
COPY . .

# Install dependencies and the package (including dev dependencies for testing)
RUN uv sync --extra dev

# Create a non-root user for security
RUN useradd -m -u 1000 slashuser && chown -R slashuser:slashuser /app
USER slashuser

# Set the default command to show help
ENTRYPOINT ["uv", "run", "slash-man"]
CMD ["--help"]

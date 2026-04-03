# Stage 1: Build the Go binary
FROM golang:1.22-alpine AS builder

WORKDIR /src

# Copy module files and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code and generated protobuf
COPY . .

# Build as a completely static binary for max compatibility in scratch containers
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /bin/service-2-go main.go

# Stage 2: Final lightweight image
FROM alpine:3.19

WORKDIR /app

# Copy the binary from the builder phase
COPY --from=builder /bin/service-2-go /app/service-2-go

# Run the ingestion engine
ENTRYPOINT ["/app/service-2-go"]

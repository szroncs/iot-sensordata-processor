# Build go binary on alpine linux
FROM golang:alpine AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Build as static binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /bin/service-2-go .

FROM alpine:3.19

WORKDIR /app

# Copy the binary from bin to app
COPY --from=builder /bin/service-2-go /app/service-2-go

# Run service
ENTRYPOINT ["/app/service-2-go"]

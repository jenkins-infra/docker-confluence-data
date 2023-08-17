variable "TAG" {
  default = ""
}

group "default" {
  targets = [
    "wiki"
  ]
}

target "wiki" {
  dockerfile = "Dockerfile"
  tags = [
    "latest",
    "${TAG}"
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}

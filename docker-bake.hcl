variable "IMAGE_NAME" {}

variable "REGISTRY" {
  default = "docker.io"
}

variable "TAG_NAME" {
  default = ""
}

# return the full image name
function "full_image_name" {
  params = [tag]
  result = notequal("", tag) ? "${REGISTRY}/${IMAGE_NAME}:${tag}" : "${REGISTRY}/${IMAGE_NAME}:latest"
}

target "default" {
  dockerfile = "Dockerfile"
  context = "."
  tags = [
    full_image_name("latest"),
    full_image_name(TAG_NAME)
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}

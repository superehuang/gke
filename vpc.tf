variable "project_id" {
    description = "project id"
  }
  
  variable "region" {
    description = "region"
  }
  
  provider "google" {
    project = var.project_id
    region  = var.region
  }


  # VPC
  resource "google_compute_network" "vpc" {
    name                    = "${random_string.random.result}vpc"
    auto_create_subnetworks = "false"
  }
  
  # Subnet
  resource "google_compute_subnetwork" "subnet" {
    name          = "${random_string.random.result}subnet"
    region        = var.region
    network       = google_compute_network.vpc.name
    ip_cidr_range = "10.10.0.0/24"
  }
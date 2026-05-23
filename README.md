# Product Management System

A simple Flask web application for managing products with web scraping, authentication, and price conversion features.

## Features

- **User Authentication**: Register and login to access the system
- **Product Management**: View, edit, and delete products
- **Web Scraping**: Automatically scrape products from a website (runs daily at 12-6 PM)
- **Price Conversion**: Track product prices in both USD and RON with automatic conversion rates
- **PDF Invoice Processing**: Upload PDF invoices and extract product data into CSV files
- **Product Filtering**: Search products by name
- **Product Sorting**: Sort products by name or price

## Installation

### 1. Clone or download the project

```bash
cd Proba_Practica
```

### 2. Install dependencies

Created with Pyton 3.12

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

The server will start at `http://localhost:5000`

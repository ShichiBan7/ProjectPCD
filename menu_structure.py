MENU_STRUCTURE = {
    "File": {
        "Open...": "file_open",
        "Save": "file_save",
        "Save As": "file_saveas",
        "-1": None,
        "Exit": "file_exit",
    },
    "Edit": {
        "Undo": "edit_undo",
        "Redo": "edit_redo",
    },
    "Basic Ops": {
        "Negative": "Negative",
        "Arithmetic": {
            "Add (+)": "Add", "Substract (-)": "Substract",
            "Multiply (*)": "Multiply", "Divide (/)": "Divide",
        },
        "Boolean": {"NOT": "NOT", "AND": "AND", "OR": "OR", "XOR": "XOR"},
        "Geometrics": {
            "Translation": "Translation", "Rotation": "Rotation",
            "Zooming": "Zooming", "Flipping": "Flipping", "Cropping": "Cropping",
        },
        "Thresholding": "Thresholding",
        "Convolution": "Convolution",
        "Fourier Transform": "Fourier Transform",
        "Colouring": {
            "Binary": "Binary", "Grayscale": "Grayscale", "RGB": "RGB",
            "HSV": "HSV", "CMY": "CMY", "YUV": "YUV", "YIQ": "YIQ",
            "Pseudo": "Pseudo",
        },
    },
    "Enhancement": {
        "Brightness": "Brightness",
        "Contrast": "Contrast",
        "Hist. Equalization": "Hist. Equalization",
        "Smoothing": {
            "Spatial Domain": {
                "Lowpass Filtering": "Lowpass Filtering",
                "Median Filtering": "Median Filtering",
            },
            "Frequency Domain": {"ILPF": "ILPF", "BLPF": "BLPF"},
        },
        "Sharpening": {
            "Spatial Domain": {
                "Highpass Filtering": "Highpass Filtering",
                "Highboost Filtering": "Highboost Filtering",
            },
            "Frequency Domain": {"IHPF": "IHPF", "BHPF": "BHPF"},
        },
        "Geometrics correction": "Geometrics correction",
    },
    "Noise": {
        "Gaussian Noise": "Gaussian Noise",
        "Rayleigh Noise": "Rayleigh Noise",
        "Erlang (Gamma) Noise": "Erlang (Gamma) Noise",
        "Exponential Noise": "Exponential Noise",
        "Uniform Noise": "Uniform Noise",
        "Impulse Noise": "Impulse Noise",
    },
    "Edge Detection Segmentation": {
        "1'st Differential Gradient": {
            "Sobel": "Sobel", "Prewitt": "Prewitt", "Robert": "Robert",
        },
        "2'nd Differential Gradient": {
            "Laplacian": "Laplacian",
            "Laplacian of Gaussian (LoG)": "Laplacian of Gaussian (LoG)",
            "Canny": "Canny",
        },
        "Compass": "Compass",
    },
    "About": {
        "Info Tim Developer": "about_info",
        "-1": None,
        "Tutorial: Link Github": "about_github",
        "Tutorial: Link Youtube": "about_youtube",
    },
}


# Teks pintasan keyboard yang ditampilkan di samping item menu.
SHORTCUT = {
    "file_open": "Ctrl+O",
    "file_save": "Ctrl+S",
    "file_saveas": "Ctrl+Shift+S",
    "file_exit": "Ctrl+Q",
    "edit_undo": "Ctrl+Z",
    "edit_redo": "Ctrl+Y",
}

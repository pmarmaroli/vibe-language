"""
Test Python file for VL conversion demo
"""

def calculate_statistics(data):
    """Calculate basic statistics from a list of numbers"""
    total = sum(data)
    count = len(data)
    average = total / count
    return average

def filter_and_process(items, threshold):
    """Filter items above threshold and double them"""
    result = []
    for item in items:
        if item > threshold:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self, name):
        self.name = name
        self.results = []
    
    def process(self, data):
        """Process data and store results"""
        for value in data:
            if value > 0:
                self.results.append(value ** 2)
        return self.results

# Test usage
if __name__ == '__main__':
    numbers = [1, 2, 3, 4, 5]
    avg = calculate_statistics(numbers)
    print(f"Average: {avg}")
    
    filtered = filter_and_process(numbers, 2)
    print(f"Filtered: {filtered}")
    
    processor = DataProcessor("test")
    processed = processor.process(numbers)
    print(f"Processed: {processed}")

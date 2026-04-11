import bcrypt
import time

def benchmark(rounds):
    password = b"secret_password"
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password, salt)
    
    start = time.time()
    for _ in range(5):
        bcrypt.checkpw(password, hashed)
    end = time.time()
    
    avg_ms = ((end - start) / 5) * 1000
    print(f"Bcrypt rounds {rounds}: Avg verification time = {avg_ms:.2f}ms")

if __name__ == "__main__":
    print("Benchmarking Bcrypt Performance...")
    # benchmark(12)  # Default - usually > 200ms
    benchmark(10)  # My new setting
    benchmark(4)   # Minimum

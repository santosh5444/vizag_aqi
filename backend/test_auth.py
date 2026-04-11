import sys
import traceback
try:
    import auth  # pyre-ignore[21]
    auth.farmer_signup('A','a@a.com','1','1')
    print("Success")
except Exception as e:
    with open('err.txt', 'w') as f:
        f.write(traceback.format_exc())

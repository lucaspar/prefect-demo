x = input()
y = input()
i = 0
exclude = []

print(("Hello, world")) # covered by ruff
if (i == 0):  # superfluous-parens not covered by ruff
    pass
if (i - 0) in exclude:  # also not covered by ruff
    pass

def my_function():
    """My docstring"""
    ...  # [unnecessary-ellipsis]

my_range = range(0, 3)  # [unnecessary-range-start]
for _ in my_range:
    ...

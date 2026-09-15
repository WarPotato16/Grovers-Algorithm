import matplotlib.pyplot as plt
import time

def visualLinear(data, target):
    n = len(data)
    plt.ion()
    fig, ax = plt.subplots()
    bars = ax.bar(range(n), data, color = ['blue'] * n)

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.set_title("Linear Search Visualization")

    for i in range(n):
        bars[i].set_color('red')
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.5)

        if data[i] == target:
            bars[i].set_color('green')
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.ioff()
            return i
    
        bars[i].set_color('blue')
    
    plt.ioff()
    return -1

dataList = [5, 1, 9, 3, 7, 6, 2, 8, 4]
searchTarget = 7

foundIndex = visualLinear(dataList, searchTarget)

if foundIndex != -1:
    print(f"Element {searchTarget} found at index {foundIndex}")
else:
    print(f"Element {searchTarget} not found in the list")
plt.show()
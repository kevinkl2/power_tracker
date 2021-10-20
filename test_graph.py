import plotext as plt
import numpy as np

l, n = 1000, 2
x = np.arange(0, l)
xticks = np.linspace(0, l - 1, 5)
xlabels = [str(i) + "π" for i in range(5)]
frames = 100

print(x)
print(xticks)
print(xlabels)

# plt.clf()
# plt.ylim(-1, 1)
# plt.xticks(xticks, xlabels)
# plt.yticks([-1, 0, 1])
# plt.plotsize(100, 30)
plt.title("Streaming Data")
plt.colorless()

for i in range(frames):
    y = plt.sin(l, n, 0, phase=2 * i / frames)
    plt.cld()
    plt.clt()
    plt.scatter(x, y, marker="dot")
    plt.sleep(0.01)
    plt.show()
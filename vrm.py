import os
import glob
import numpy as np
from matplotlib import pyplot as plt

class Context:
	def __init__(self) -> None:
		self.data = np.array([])
		self.filtered = np.array([])

def status(context: Context) -> tuple[int, int]:
	row, col = context.filtered.shape
	print(f"now shape {row}x{col}")
	return row, col

def preview_impl(context: Context, max_lines: int = 10) -> None:
	row, col = status(context)
	for i in range(min(row, max_lines)):
		print(context.filtered[i, :])
	return

def preview(context: Context, args: list[str]) -> None:
	if args == []:
		preview_impl(context)
	else:
		preview_impl(context, int(args[0]))
	return

def load(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [file]")
	
	path = args[0]
	if not os.path.isfile(path):
		possible_paths = glob.glob(path)
		if possible_paths == []:
			possible_paths = glob.glob(f"{path}.*")
		if possible_paths == []:
			raise Exception("file not found")
		path = possible_paths[0]
	
	print(f"Loading {path}")
	with open(path, "r") as f:
		data = []
		for row, line in enumerate(f):
			try:
				data.append(list(map(float, line.split())))
			except ValueError as e:
				print(f"Warning: on line {row}, {e}, skipped.")
				continue
		context.data = np.array(data)
		context.filtered = context.data.copy()
	
	preview_impl(context)
	return

def filter(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [filter type]")
	
	filter_type = args[0].lower()
	if filter_type == "row":
		filter_row(context, args[1:])
	elif filter_type == "col":
		filter_col(context, args[1:])
	elif filter_type == "clean":
		filter_clean(context, args[1:])
	else:
		raise Exception("Unknown filter type")
	preview_impl(context)
	return

def filter_clean(context: Context, args: list[str]) -> None:
	print("filter cleaned")
	context.filtered = context.data.copy()
	return

def filter_row(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [filter type]")
	
	filter_type = args[0].lower()
	if filter_type == "idx":
		filter_row_idx(context, args[1:])
	elif filter_type == "range":
		filter_row_range(context, args[1:])
	elif filter_type == "expr":
		raise Exception("TODO")
	else:
		raise Exception("Unknown filter type")
	return

def filter_col(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [filter type]")
	
	filter_type = args[0].lower()
	if filter_type == "idx":
		filter_col_idx(context, args[1:])
	elif filter_type == "range":
		filter_col_range(context, args[1:])
	elif filter_type == "expr":
		raise Exception("TODO")
	else:
		raise Exception("Unknown filter type")
	return

def filter_row_idx(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [idx]")
	
	idxs = eval(args[0])
	if isinstance(idxs, int):
		idxs = (idxs,)
	context.filtered = np.concatenate([context.filtered[idx: idx+1, :] for idx in idxs], axis=0)
	return

def parse_range(range_str: str) -> tuple[int, int]:
	if ':' in range_str:
		range_pair = range_str.split(':')
	elif '-' in range_str:
		range_pair = range_str.split('-')
	elif ',' in range_str:
		range_pair = range_str.split(',')
	else:
		raise Exception("Unknown range format")
	if len(range_pair) != 2:
		raise Exception("Unknown range format")
	
	start, end = int(range_pair[0]), int(range_pair[1])
	return start, end

def filter_row_range(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [range]")
	
	range_str = args[0]
	start, end = parse_range(range_str)

	print(f"filter row by range {start}: {end}")
	context.filtered = context.filtered[start:end, :]
	return

def filter_col_idx(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [idx]")
	
	idxs = eval(args[0])
	if isinstance(idxs, int):
		idxs = (idxs,)
	context.filtered = np.concatenate([context.filtered[:, idx: idx+1] for idx in idxs], axis=1)
	return

def filter_col_range(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [range]")
	
	range_str = args[0]
	start, end = parse_range(range_str)

	print(f"Filter col by range {start}: {end}")
	context.filtered = context.filtered[:, start:end]
	return

def show(context: Context, args: list[str]) -> None:
	if args == []:
		idx_x, idx_y = 0, 1
	elif len(args) < 2:
		raise Exception("expected parameter [idx_x] [idx_y]")
	else:
		idx_x, idx_y = args[:2]
		if idx_x != "line":
			idx_x = int(idx_x)
		if idx_y != "line":
			idx_y = int(idx_y)
	
	row, col = status(context)
	
	X = context.filtered[:, idx_x] if idx_x != "line" else np.arange(row)
	Y = context.filtered[:, idx_y] if idx_y != "line" else np.arange(col)

	print("Showing...")
	plt.cla()
	plt.plot(X, Y, 'o')
	plt.show()
	return

def save(context: Context, args: list[str]) -> None:
	if args == []:
		raise Exception("missing parameter [path]")
	
	path = args[0]
	print(f"Saving {path}")
	with open(path, "w") as f:
		for row in context.filtered:
			f.write(' '.join([str(item) for item in row]) + '\n')
	return


def main_loop():
	context = Context()
	while True:
		try:
			cmd = input("/> ")
			cmd = [word.strip() for word in cmd.split()]
			if len(cmd) == 0:
				continue
			op = cmd[0].lower()
			if op == "exit":
				print("Bye!")
				break
			elif op == "help":
				print("help: TODO") # TODO
			elif op == "load":
				load(context, cmd[1:])
			elif op == "status":
				status(context)
			elif op == "preview":
				preview(context, cmd[1:])
			elif op == "filter":
				filter(context, cmd[1:])
			elif op == "show":
				show(context, cmd[1:])
			elif op == "save":
				save(context, cmd[1:])
			else:
				raise Exception("Unknown command")
		except EOFError:
			print("Bye!")
			break
		except Exception as e:
			print(f"Error: {e}")
			continue
		except KeyboardInterrupt:
			print()
			continue
	return


if __name__ == "__main__":
	main_loop()
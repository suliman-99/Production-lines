from numpy import sum
from typing import TextIO

def read_tasks_times() -> dict[int, int]:
    tasks_times = {}
    with open("tasks.txt", "r") as file:
        tasks = file.readlines()
        for line in tasks:
            task_id, task_time = line.strip().split(",")
            task_id = int(task_id)
            task_time = int(task_time)
            tasks_times[task_id] = task_time
    return tasks_times

def read_links(tasks_times:dict[int, int]) -> dict[int, list[int]]:
    links = {}
    with open("tasks_links.txt", "r") as file:
        task_links = file.readlines()
        for line in task_links:
            source_id, target_id = line.strip().split(",")
            source_id = int(source_id)
            target_id = int(target_id)
            if links.get(source_id, None) is None:
                links[source_id] = []
            links[source_id].append(target_id)
    for task_id in tasks_times.keys():
        if not links.get(task_id):
            links[task_id] = []
    return links

class ProductionLine:
    def __init__(self, tasks_ids:list[int], total_time, average_time:float, idx:int) -> None:
        self.tasks_ids = tasks_ids
        self.total_time = total_time
        self.diff = abs(average_time-self.total_time)
        self.idx = idx


    def write(self, writable_file:TextIO) -> None:
        writable_file.write(f'{self.idx} : {self.tasks_ids} Total Time=({self.total_time}), dif={round(self.diff, 2)} \n')


class Solution:
    def __init__(self, production_lines:list[ProductionLine], total_time:int, average_time:int, idx:int) -> None:
        self.production_lines = production_lines
        self.total_time = total_time
        self.average_time = average_time
        self.idx = idx

        self.total_diff = 0
        self.min_time = self.production_lines[0].total_time
        self.max_time = self.production_lines[0].total_time

        for production_line in production_lines:
            self.total_diff += production_line.diff
            self.min_time = min(self.min_time, production_line.total_time)
            self.max_time = max(self.max_time, production_line.total_time)

        self.average_diff = self.max_time/len(self.production_lines)

    def write(self, writable_file:TextIO) -> None:
        writable_file.write(f'Solution {self.idx} : \n')

        for production_line in self.production_lines:
            production_line.write(writable_file)

        writable_file.write(f'Total Time = {self.total_time} \n')
        writable_file.write(f'Total_Time/Steps = {round(self.average_time, 2)} \n')
        writable_file.write(f'Total differences = {round(self.total_diff, 2)} \n')
        writable_file.write(f'Average differences = {round(self.average_diff, 2)} \n')
        writable_file.write(f'Max Time = {self.max_time} \n')
        writable_file.write(f'Min Time = {self.min_time} \n')
        
        writable_file.write(' ---------------------------------------------------------------------------- \n')


def generate_all_sorted_tasks(links:dict[int ,list[int]], need:dict[int, int], all_sorted_tasks:list[list[int]], sorted_tasks:list[int]):
    
    if len(sorted_tasks) == len(links):
        all_sorted_tasks.append(sorted_tasks)
        return
    
    for cur in links.keys():
        if not need[cur] and cur not in sorted_tasks:

            new_sorted_tasks = sorted_tasks.copy()
            new_sorted_tasks.append(cur)

            new_need = need.copy()
            for child in links[cur]:
                new_need[child] -= 1

            generate_all_sorted_tasks(links, new_need, all_sorted_tasks, new_sorted_tasks)


def generate_all_cuts(size:int, steps:int, all_cuts:list[list[int]], cut:list[int]):

    if len(cut) == steps:
        cut.append(size)
        all_cuts.append(cut)
        return
    
    for i in range(cut[-1], size+1):
        new_cut = cut.copy()
        new_cut.append(i)
        generate_all_cuts(size, steps, all_cuts, new_cut)


def get_all_solutions(tasks_times:dict[int, int], links:dict[int, list[int]], steps:int) -> list[Solution]:
    total_time = sum([task_time for task_time in tasks_times.values()], dtype=int)
    average_time = total_time/steps
    
    need = {}
    for task_id in tasks_times.keys():
        need[task_id] = 0
    for children in links.values():
        for child in children:
            need[child] += 1
            
    all_sorted_tasks = []
    generate_all_sorted_tasks(links, need, all_sorted_tasks, [])

    all_cuts = []
    generate_all_cuts(len(tasks_times), steps, all_cuts, [0])

    solutions = []
    for sorted_tasks in all_sorted_tasks:
        for cut in all_cuts:
            production_lines = []
            for i in range(len(cut)-1):
                cur_tasks_ids = sorted_tasks[cut[i]:cut[i+1]]
                cur_total_time = sum([tasks_times[task_id] for task_id in cur_tasks_ids],  dtype=int)
                production_lines.append(
                    ProductionLine(
                        cur_tasks_ids,
                        cur_total_time,
                        average_time,
                        i+1,
                    )
                )
            solutions.append(
                Solution(
                    production_lines,
                    total_time,
                    average_time,
                    len(solutions),
                )
            )
            
    return solutions


def get_best_solution(solutions:list[Solution]) -> Solution:
    best_solution = solutions[0]
    for solution in solutions:
        if solution.total_diff < best_solution.total_diff:
            best_solution = solution
    return best_solution


def write_solution_list(solutions:list[Solution], file_name:str) -> None:
    with open(file_name, "w") as writable_file:
        for solution in solutions:
            solution.write(writable_file)


def write_solution(solution:Solution, file_name:str) -> None:
    with open(file_name, "w") as writable_file:
        solution.write(writable_file)


def main():

    tasks_times = read_tasks_times()
    links = read_links(tasks_times)

    # steps = int(input('Enter Setps: '))
    steps = 3

    solutions = get_all_solutions(tasks_times, links, steps)
    write_solution_list(solutions, ' all_results_steps.txt')

    best_solution = get_best_solution(solutions)
    write_solution(best_solution, 'optimal_results_steps.txt')


if __name__ == '__main__':
    main()




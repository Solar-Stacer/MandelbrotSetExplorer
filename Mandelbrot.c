#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <time.h>

int SCENE_WIDTH, SCENE_HEIGHT;
double MBS_MIN_X, MBS_MAX_X;
double MBS_MIN_Y, MBS_MAX_Y;
double MINIMUM_ITERATION;
double DEPTH_FACTOR;
double DEPTH_BASE;

/*
printf("SCENE_WIDTH:    %d \n", SCENE_WIDTH);
printf("SCENE_HEIGHT:   %d \n", SCENE_HEIGHT);
printf("MBS_MIN_X:      %f \n", MBS_MIN_X);
printf("MBS_MAX_X:      %f \n", MBS_MAX_X);
printf("MBS_MIN_Y:      %f \n", MBS_MIN_Y);
printf("MBS_MAX_Y:      %f \n", MBS_MAX_Y);
*/

void set_global_settings(int scene_width, int scene_height,
                         double mbs_min_x, double mbs_max_x,
                         double mbs_min_y, double mbs_max_y,
                         double depth_factor, double minimum_iteration,
                         double depth_base)
{
    SCENE_WIDTH = scene_width;
    SCENE_HEIGHT = scene_height;
    MBS_MIN_X = mbs_min_x;
    MBS_MAX_X = mbs_max_x;
    MBS_MIN_Y = mbs_min_y;
    MBS_MAX_Y = mbs_max_y;
    DEPTH_FACTOR = depth_factor;
    MINIMUM_ITERATION = minimum_iteration;
    DEPTH_BASE = depth_base;
}

static inline double log_b(double x, double base)
{
    return (double)log(x) / log(base);
}

static inline int set_max_iteration(double zoom)
{
    double depth = -log_b(zoom, DEPTH_BASE);

    int iterations =
        MINIMUM_ITERATION + (int)(depth * DEPTH_FACTOR);

    if (iterations < MINIMUM_ITERATION)
        iterations = MINIMUM_ITERATION;

    return (int)iterations;
}

static inline int mandelbrot_point(double x0, double y0, int max_iter)
{
    double x = 0, y = 0;
    double x2 = 0, y2 = 0;
    int iteration = 0;

    while (x2 + y2 <= 4 && iteration < max_iter)
    {
        x2 = x * x;
        y2 = y * y;
        y = 2 * x * y + y0;
        x = x2 - y2 + x0;
        iteration++;
    }

    return iteration;
}

static inline int mandelbrot_interior(double x, double y)
{
    double x_minus = x - 0.25f;
    double q = x_minus * x_minus + y * y;

    if (q * (q + x_minus) <= 0.25f * y * y)
        return 1;

    double x_plus = x + 1.0f;

    if (x_plus * x_plus + y * y <= 0.0625f)
        return 1;

    return 0;
}

void set_mandelbrot_point(uint8_t *grid, int width, int height, double moved_by_x, double moved_by_y, double zoom)
{
    clock_t start = clock();
    srand(time(NULL));

    int max_iteration = set_max_iteration(zoom);
    printf("max_iteration: %d\n", max_iteration);

    double min_x = moved_by_x + MBS_MIN_X * zoom;
    double max_x = moved_by_x + MBS_MAX_X * zoom;

    double min_y = moved_by_y + MBS_MIN_Y * zoom;
    double max_y = moved_by_y + MBS_MAX_Y * zoom;

    double dx = (max_x - min_x) / (width - 1);
    double dy = (max_y - min_y) / (height - 1);

#pragma omp parallel for schedule(dynamic, 1)
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            uint8_t color;
            double color_value = 0;
            /*
            double samples = 8.0;
            for (int i = 0; i < samples; i++)
            {
                double scaled_y = min_y + (y + (double)rand() / RAND_MAX) * dy;
                double scaled_x = min_x + (x + (double)rand() / RAND_MAX) * dx;

                int result;

                if (mandelbrot_interior(scaled_x, scaled_y))
                    result = max_iteration;
                else
                    result = mandelbrot_point(scaled_x, scaled_y, max_iteration);

                if (result == max_iteration)
                    color_value += 0.0;
                else
                    color_value += 255.0 * log_base(result, 1.1) / log_base(max_iteration, 1.1);
            }
            color_value = color_value / samples;
            */

            double scaled_y = min_y + y * dy;
            double scaled_x = min_x + x * dx;

            int result;

            if (mandelbrot_interior(scaled_x, scaled_y))
                result = max_iteration;
            else
                result = mandelbrot_point(scaled_x, scaled_y, max_iteration);

            if (result == max_iteration)
                color_value += 0.0;
            else
                color_value += 255.0 * log_b(result, 1.1) / log_b(max_iteration, 1.1);

            color_value = color_value;

            color = (uint8_t)(color_value);

            int i = (y * width + x) * 3;

            grid[i] = color;
            grid[i + 1] = color;
            grid[i + 2] = color;
        }
    }
    clock_t end = clock();
    double cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;

    printf("CPU time used: %f seconds\n\n", cpu_time_used);
}
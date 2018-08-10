import matplotlib
import matplotlib.pyplot as plt # without this, matplotlib.style.use crashes with AttributeError
from matplotlib.backends.backend_pdf import PdfPages

from images import format_ax


matplotlib.style.use('ggplot')

# The default figsize is the size of an A4 sheet in inches
A4_SIZE_PORTRAIT = [8.27, 11.7]
TITLE_FONT_SIZE = 12


# -----------------------------------------------------
# PDF


def save_plots_as_pdf(df, filename, nrows=3, ncols=2, figsize=A4_SIZE_PORTRAIT,
                      title_font_size=TITLE_FONT_SIZE):
    vars_ = df.columns
    nvars = len(vars_)
    vars_per_page = nrows * ncols
    with PdfPages(filename) as pdf:
        for start_index in range(0, nvars, vars_per_page):
            page_vars = vars_[start_index:start_index + vars_per_page]
            _ = many_plots_per_page(df[page_vars], nrows, ncols, figsize, title_font_size)
            pdf.savefig()
            plt.close()


def many_plots_per_page(df, nrows, ncols, figsize=A4_SIZE_PORTRAIT, title_font_size=TITLE_FONT_SIZE):
    page_vars = df.columns

    # The following command uses the built-in Pandas mechanism for placing subplots on a page.
    # It automatically increases spacing between subplots and rotates axis ticks if they
    # take up too much space. However, this mechanism is broken in Pandas < 0.17.
    # See: https://github.com/pydata/pandas/issues/11536
    # It also cannot handle multiple variables per subplot, so if we want that, we'll have to
    # replicate parts of the Pandas implementation or write our own.
    axes = df.plot(subplots=True, layout=(nrows, ncols), legend=None, figsize=figsize)

    # Now removing axis labels and adding plot titles.
    for i, axes_row in enumerate(axes):
        for j, ax in enumerate(axes_row):
            var_idx = i * ncols + j
            if var_idx >= len(page_vars):
                # We're at the end of the last page, which is not filled completely.
                break
            ax.set_title(page_vars[var_idx], fontsize=title_font_size)
            format_ax(ax)
    return axes


if __name__== '__main__':
    import access
    dfm = access.get_dataframe('m')    
    save_plots_as_pdf(dfm, 'plt.pdf')
    

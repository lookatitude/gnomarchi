-- gnomarchi neovim seed (not omarchy-nvim). Theme colors applied via
-- ~/.config/nvim/gnomarchi-colors.vim from `gnomarchi theme set`.
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.termguicolors = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.clipboard = "unnamedplus"

local colors = vim.fn.stdpath("config") .. "/gnomarchi-colors.vim"
if vim.fn.filereadable(colors) == 1 then
  vim.cmd("source " .. colors)
end

vim.keymap.set("n", "<leader>ff", ":edit .<CR>", { desc = "browse cwd" })

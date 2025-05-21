using System;
using System.Windows.Input;

namespace WarmUp.Core
{
    class RelayCommand : ICommand
    {
        private readonly Func<Task> _executeAsync; // Hỗ trợ async không tham số
        private readonly Action<object> _execute;  // Hỗ trợ đồng bộ có tham số
        private readonly Func<object, bool>? _canExecute;

        // Constructor cho async không tham số
        public RelayCommand(Func<Task> executeAsync, Func<object, bool>? canExecute = null)
        {
            _executeAsync = executeAsync ?? throw new ArgumentNullException(nameof(executeAsync));
            _canExecute = canExecute;
        }

        // Constructor cho đồng bộ có tham số
        public RelayCommand(Action<object> execute, Func<object, bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        event EventHandler ICommand.CanExecuteChanged
        {
            add { CommandManager.RequerySuggested += value; }
            remove { CommandManager.RequerySuggested -= value; }
        }

        public bool CanExecute(object parameter)
        {
            return _canExecute == null || _canExecute(parameter);
        }

        public async void Execute(object parameter)
        {
            if (_executeAsync != null)
            {
                await _executeAsync();
            }
            else if (_execute != null)
            {
                _execute(parameter);
            }
        }
    }
}
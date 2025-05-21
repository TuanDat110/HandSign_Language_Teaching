using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using WarmUp.Core;

namespace WarmUp.MVVM.ViewModel
{
    class Alphabet_Page3 : InotifyChanged
    {
        private string _alphabet;
        private string _imagehandsign;
        private string _imageanimal;
        public ICommand Onboarding { get; set; }
        public Alphabet_Page3()
        {
            Onboarding = new RelayCommand(ShowAlphabet);
        }
        public string ImageLetter
        {
            get => _alphabet;
            set
            {
                if (_alphabet != value)
                {
                    _alphabet = value;
                    OnpropertyChanged();
                }
            }
        }

        public string ImageHandsign
        {
            get => _imagehandsign;
            set
            {
                if (_imagehandsign != value)
                {
                    _imagehandsign = value;
                    OnpropertyChanged();
                }
            }
        }
        public string ImageAnimal
        {
            get => _imageanimal;
            set
            {
                if (_imageanimal != value)
                {
                    _imageanimal = value;
                    OnpropertyChanged();
                }
            }
        }
        public void ShowAlphabet(object parameter)
        {
            if (parameter is string letter)
            {
                string text = letter;
                ImageLetter = $"D:\\install\\doan1\\WarmUp\\WarmUp\\Image\\Trang3_1\\Text\\{text}_text.png";
                ImageHandsign= $"D:\\install\\doan1\\WarmUp\\WarmUp\\Image\\Trang3_1\\handsign\\{text}_handsign.jpg";
                ImageAnimal = $"D:\\install\\doan1\\WarmUp\\WarmUp\\Image\\Trang3_1\\Animal\\{text}_animal.png";
            }

        }
    }
}

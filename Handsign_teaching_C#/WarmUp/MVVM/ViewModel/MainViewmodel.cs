using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.Serialization.DataContracts;
using System.Text;
using System.Threading.Tasks;
using WarmUp.Core;
using WarmUp.MVVM.View;

namespace WarmUp.MVVM.ViewModel
{
    internal class MainViewmodel : InotifyChanged
    {
        public RelayCommand GotoMain { get; set; }
        public RelayCommand GotoView2 { get; set; }
        public RelayCommand Gotopage3 { get; set; }
        public RelayCommand Gotopage4 { get; set; }
        //public RelayCommand Gotopage5 { get; set; }
        public GiaoDienChinh giaodien { get; set; }
        public BaseView baseview { get; set; }
        public Page3 page3 { get; set; }
        public Page4 page4 { get; set; }
        //public Page5 page5 { get; set; }

        private object _currentview;
        public object Currentview
        {
            get { return _currentview; }
            set
            {
                _currentview = value;
                Debug.WriteLine("!ok");
                 OnpropertyChanged();
            }

        }
        public MainViewmodel()
        {
            baseview = new BaseView();
            Currentview = baseview;
            giaodien = new GiaoDienChinh();
            page3 = new Page3();
            page4 = new Page4();
            //page5 = new Page5();

            GotoMain = new RelayCommand(o =>
            {
                Debug.WriteLine("oke");
                Currentview = baseview;
            });
            GotoView2 = new RelayCommand(o =>
            {
                Debug.WriteLine("kkkk");
                Currentview = giaodien;
            });
            Gotopage3 = new RelayCommand(o => {
                Debug.WriteLine("Chuyen sang page3");
                Currentview = page3;
            });
            Gotopage4 = new RelayCommand(o => {
                Debug.WriteLine("Chuyen sang page4");
                Currentview = page4;
            });
            //Gotopage5 = new RelayCommand(o => {
            //    Currentview = page5;
            //});
        }
    }
}

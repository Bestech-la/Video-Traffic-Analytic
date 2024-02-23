import * as yup from 'yup';

export const schema = yup.object().shape({
  yOne: yup.number().required('ກະລຸນາກໍານຸດຕີນໄຟແດງ'),
  yTwo: yup.number().required('ກະລຸນາກໍານຸດຫົວໄຟແດງ'),
  date_time: yup.string().required("ກະລຸນາເລືອກເວລາ"),
  algorithm: yup.string().required("ກະລຸນາເລືອກປະເພດ Algorithm"),
  video: yup.mixed().required("ກະລຸນາປ້ອນອັບໂຫຼດຮູບພາບ"),
});


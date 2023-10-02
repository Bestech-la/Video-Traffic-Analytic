import * as yup from 'yup';

// // Define the maximum file size in bytes (500 MB)
// const MAX_FILE_SIZE = 500 * 1024 * 1024; 
// const validFileExtensions = ['mp4'];


// async function isValidFileType(value: File | undefined, allowedExtensions: string[]): Promise<boolean> {
//   if (!value || !value.name) return false; 
//   const extension = value.name.split('.').pop()?.toLowerCase();
//   return extension ? allowedExtensions.includes(extension) : false;
// }


export const schema = yup.object().shape({
  location_name: yup.string().required('ສະຖານທີ'),
  // yOne: yup.number().required('y 1'),
  // yTwo: yup.number().required('y 2'),
  // video: yup.object().shape({
  //   video: yup
  //     .mixed()
  //     .required("Video file is required")
  //     .test("Not a valid video type", (value) =>
  //  console.log("value",value)
  //     )
  //     .test("is-valid-size", "Max allowed size is 500 MB", (value) =>
  //       value && value.size <= MAX_FILE_SIZE
  //     ),
  // }),
});

// isValidFileType(value?.name?.toLowerCase(), validFileExtensions)
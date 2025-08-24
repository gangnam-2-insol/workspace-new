import React from 'react';
import { FiX } from 'react-icons/fi';
import * as S from '../styles';

/**
 * props:
 *   title: string
 *   onClose: () => void
 *   children: JSX.Element
 */
const BaseModal = ({ title, onClose, children }) => (
  <S.ModalOverlay
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    onClick={onClose}
  >
    <S.ModalContent
      initial={{ scale: 0.9 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0.9 }}
      onClick={e => e.stopPropagation()}
    >
      <S.ModalHeader>
        <S.ModalTitle>{title}</S.ModalTitle>
        <S.ModalCloseButton onClick={onClose}>
          <FiX />
        </S.ModalCloseButton>
      </S.ModalHeader>
      {children}
    </S.ModalContent>
  </S.ModalOverlay>
);

export default BaseModal;
